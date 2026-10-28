from accounts.models import User
from tenants.models import Tenant
from contracts.models import Contract
from payments.models import Payment
from .base import DomainTestCase


class TenantPortalTests(DomainTestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', role='tenant', tenant=self.tenant)
        other = Tenant.objects.create(full_name='PRIVATE-OTHER', phone='0900000099', identity_number='000000000099', address='Other')
        self.other_contract = Contract.objects.create(code='PRIVATE-CONTRACT', tenant=other, apartment=self.apartment,
            start_date=self.contract.start_date, end_date=self.contract.end_date, status='draft')
        self.client.force_login(self.customer)

    def test_all_sections_hide_other_tenants(self):
        for section in ('overview', 'apartment', 'contracts', 'payments', 'maintenance', 'notifications'):
            page = self.client.get('/my-home/', {'section': section})
            self.assertEqual(page.status_code, 200)
            self.assertNotContains(page, 'PRIVATE-CONTRACT')
            self.assertNotContains(page, 'PRIVATE-OTHER')

    def test_profile_cannot_change_role_or_link(self):
        page = self.client.post('/accounts/profile/', {'full_name': 'Updated Name', 'phone': '0900000002',
            'email': 'updated@example.com', 'address': 'Updated address', 'role': 'manager',
            'tenant': self.other_contract.tenant_id, 'identity_number': '000000000099'})
        self.assertEqual(page.status_code, 302)
        self.customer.refresh_from_db()
        self.tenant.refresh_from_db()
        self.assertEqual(self.customer.role, 'tenant')
        self.assertEqual(self.customer.tenant_id, self.tenant.pk)
        self.assertEqual(self.tenant.identity_number, '000000000001')
        self.assertEqual(self.tenant.full_name, 'Updated Name')
