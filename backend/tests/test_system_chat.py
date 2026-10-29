from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import override_settings

from accounts.models import User
from buildings.models import Apartment, Amenity, ApartmentAmenity
from contracts.models import Contract
from maintenance.models import MaintenanceRequest
from payments.models import Payment
from tenants.models import Tenant
from ai_assistant.services.chatbot_service import answer_question
from ai_assistant.services.system_lookup import answer_system_question
from .base import DomainTestCase


class SystemChatTests(DomainTestCase):
    def setUp(self):
        cache.clear()
        self.customer = User.objects.create_user(username='customer', role='tenant', tenant=self.tenant)
        self.other = User.objects.create_user(username='unlinked', role='tenant')
        self.free = Apartment.objects.create(building=self.building, code='FREE', rent=7000000, area=40, is_listed=True)
        self.hidden = Apartment.objects.create(building=self.building, code='SECRET', rent=6000000, area=40)
        self.expensive = Apartment.objects.create(building=self.building, code='HIGH', rent=10000000, area=60, is_listed=True)
        self.payment = Payment.objects.create(contract=self.contract, amount=5000000, kind='rent', due_date=self.today, status='pending')

    def ask(self, question, user=None):
        return answer_system_question(question, user or self.customer)

    def test_catalogue_price_and_visibility(self):
        result = self.ask('Có căn hộ nào còn trống dưới 8 triệu không?')
        self.assertIn('FREE', result['answer'])
        for hidden in ('SECRET', 'HIGH', 'A101'):
            self.assertNotIn(hidden, result['answer'])
        self.assertIn('Dữ liệu hệ thống', result['sources'][0]['title'])
        self.assertIn('SECRET', self.ask('Căn hộ nào còn trống dưới 8 triệu?', self.manager)['answer'])
        self.assertNotIn('SECRET', self.ask('Căn hộ nào còn trống dưới 8 triệu?', self.accountant)['answer'])

    def test_maintenance_units_and_inactive_buildings_not_offered(self):
        self.free.status = 'maintenance'; self.free.save()
        self.assertNotIn('FREE', self.ask('Căn hộ nào còn trống?')['answer'])
        self.building.is_active = False; self.building.save()
        self.assertNotIn('HIGH', self.ask('Căn hộ nào còn trống?')['answer'])

    def test_own_contract_and_other_contract_isolation(self):
        self.assertIn(self.contract.code, self.ask('Hợp đồng của tôi hết hạn ngày nào?')['answer'])
        other_tenant = Tenant.objects.create(full_name='Other resident', identity_number='000000000099', phone='0000000099', address='Demo')
        self.other.tenant = other_tenant
        self.other.save()
        foreign = Contract.objects.create(code='HD-PRIVATE-999', apartment=self.hidden, tenant=other_tenant,
            start_date=self.today, end_date=self.today + timedelta(days=60), status='draft')
        # Another tenant's contract must not be exposed even with its exact code.
        self.assertNotIn(foreign.code, self.ask('Hợp đồng HD-PRIVATE-999 hết hạn ngày nào?')['answer'])
        self.assertIn(foreign.code, self.ask('Hợp đồng của tôi hết hạn ngày nào?', self.other)['answer'])
        self.assertNotIn(self.contract.code, self.ask('Hợp đồng của tôi hết hạn ngày nào?', self.other)['answer'])

    def test_contract_current_and_expiring(self):
        result = self.ask('Danh sách hợp đồng sắp hết hạn', self.manager)
        self.assertIn(self.contract.code, result['answer'])

    def test_finance_roles_and_tenant_scope(self):
        for user in (self.customer, self.manager, self.accountant):
            self.assertIn('5.000.000 đồng', self.ask('Tháng này tôi còn nợ bao nhiêu?', user)['answer'])
        self.assertEqual(self.ask('Công nợ hiện tại', self.staff)['sources'], [])
        result = self.ask('Công nợ hợp đồng TEST-001', self.other)
        self.assertNotIn('5.000.000', result['answer'])

    def test_month_kind_and_paid_filters(self):
        Payment.objects.create(contract=self.contract, amount=300000, kind='service', due_date=self.today, status='pending')
        Payment.objects.create(contract=self.contract, amount=900000, kind='rent', due_date=self.today - timedelta(days=40), status='paid', paid_date=self.today)
        result = self.ask(f'Tiền thuê chưa thanh toán tháng {self.today.month}/{self.today.year}')
        self.assertIn('5.000.000 đồng', result['answer'])
        self.assertNotIn('300.000', result['answer'])
        self.assertIn('900.000', self.ask('Các khoản đã thanh toán của tôi')['answer'])
        self.assertEqual(self.ask('Công nợ tháng 13/2026')['sources'], [])

    def test_total_includes_rows_beyond_display_limit(self):
        for i in range(12):
            Payment.objects.create(contract=self.contract, amount=1000, kind='service',
                due_date=self.today - timedelta(days=i + 1), status='pending')
        result = self.ask('Tôi còn nợ bao nhiêu?')
        self.assertIn('5.012.000 đồng', result['answer'])
        self.assertIn('13 khoản', result['answer'])
        self.assertEqual(len([line for line in result['answer'].splitlines() if line.startswith('- ')]), 10)

    def test_only_own_submitted_maintenance_visible(self):
        MaintenanceRequest.objects.create(apartment=self.apartment, submitted_by=self.customer, content='OWN-ISSUE', status='processing')
        MaintenanceRequest.objects.create(apartment=self.apartment, submitted_by=self.staff, content='PRIVATE-ISSUE')
        result = self.ask('Yêu cầu bảo trì của tôi xử lý đến đâu?')
        self.assertIn('OWN-ISSUE', result['answer'])
        self.assertNotIn('PRIVATE-ISSUE', result['answer'])
        self.assertIn('Đang xử lý', result['answer'])
        self.assertEqual(self.ask('Danh sách bảo trì', self.accountant)['sources'], [])

    def test_amenities_are_actual_unit_equipment_not_invented_common_facilities(self):
        amenity = Amenity.objects.create(name='Máy giặt kiểm thử')
        ApartmentAmenity.objects.create(apartment=self.free, amenity=amenity, quantity=1)
        result = self.ask('Tòa nhà có những tiện ích gì?')
        self.assertIn('Máy giặt kiểm thử × 1', result['answer'])
        self.assertIn('chưa có danh mục tiện ích chung', result['answer'])

    def test_no_lookup_without_authenticated_active_user(self):
        self.assertIsNone(answer_system_question('Công nợ hiện tại', AnonymousUser()))
        self.customer.is_active = False
        self.assertIsNone(self.ask('Công nợ hiện tại'))

    def test_policy_questions_continue_using_documents(self):
        for question in ('Quy trình hoàn cọc', 'Thanh toán tiền thuê khi nào?', 'Làm sao báo hỏng?', 'Bảo trì phản hồi trong bao lâu?'):
            self.assertIsNone(self.ask(question))

    @override_settings(AI_PROVIDER='disabled')
    @patch('ai_assistant.services.chatbot_service.generate_json')
    def test_live_lookup_needs_no_external_api_and_is_read_only(self, generate):
        before = (Contract.objects.count(), Payment.objects.count(), self.payment.status)
        result = answer_question('Tháng này tôi còn nợ bao nhiêu?', user=self.customer)
        self.assertIn('5.000.000', result['answer'])
        self.payment.refresh_from_db()
        self.assertEqual(before, (Contract.objects.count(), Payment.objects.count(), self.payment.status))
        generate.assert_not_called()

    def test_json_endpoint_uses_request_user(self):
        self.client.force_login(self.other)
        result = self.client.post('/ai/chatbot/', {'question': 'Hợp đồng của tôi hết hạn ngày nào?'}, HTTP_ACCEPT='application/json')
        self.assertEqual(result.status_code, 200)
        self.assertNotIn(self.contract.code, result.json()['answer'])
