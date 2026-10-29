from datetime import timedelta

from buildings.models import Apartment, Building
from contracts.forms import ContractForm
from contracts.models import Contract
from .base import DomainTestCase


class ContractApartmentChoicesTests(DomainTestCase):
    def setUp(self):
        self.free = Apartment.objects.create(building=self.building, code='FREE', area=40, rent=6000000)

    def test_new_form_hides_occupied_maintenance_and_inactive_buildings(self):
        maintenance = Apartment.objects.create(building=self.building, code='FIX', area=40, rent=6000000, status='maintenance')
        building = Building.objects.create(name='Closed', address='Test', is_active=False)
        closed = Apartment.objects.create(building=building, code='CLOSED', area=40, rent=6000000)
        choices = ContractForm(actor=self.manager).fields['apartment'].queryset
        self.assertIn(self.free, choices)
        for apartment in (self.apartment, maintenance, closed):
            self.assertNotIn(apartment, choices)

    def test_edit_keeps_own_apartment(self):
        form = ContractForm(instance=self.contract, actor=self.manager)
        self.assertIn(self.apartment, form.fields['apartment'].queryset)

    def test_submitted_occupied_apartment_is_rejected(self):
        data = {'code': 'NEW', 'apartment': self.apartment.pk, 'tenant': self.tenant.pk,
                'start_date': self.today, 'end_date': self.today + timedelta(days=60), 'status': 'active'}
        form = ContractForm(data=data, actor=self.manager)
        self.assertFalse(form.is_valid())
        self.assertIn('apartment', form.errors)
        data['apartment'] = self.free.pk
        self.assertTrue(ContractForm(data=data, actor=self.manager).is_valid())

    def test_future_booking_excluded_for_submitted_overlap(self):
        Contract.objects.create(code='FUTURE', apartment=self.free, tenant=self.tenant,
            start_date=self.today + timedelta(days=30), end_date=self.today + timedelta(days=90), status='active')
        self.assertIn(self.free, ContractForm(actor=self.manager).fields['apartment'].queryset)
        data = {'code': 'NEW', 'apartment': self.free.pk, 'tenant': self.tenant.pk,
                'start_date': self.today, 'end_date': self.today + timedelta(days=40), 'status': 'active'}
        form = ContractForm(data=data, actor=self.manager)
        self.assertNotIn(self.free, form.fields['apartment'].queryset)
        self.assertFalse(form.is_valid())

    def test_ended_and_terminated_contracts_do_not_hide_available_units(self):
        self.contract.end_date = self.today - timedelta(days=1)
        self.contract.save()
        self.assertIn(self.apartment, ContractForm(actor=self.manager).fields['apartment'].queryset)
        self.contract.status = 'terminated'
        self.contract.end_date = self.today + timedelta(days=20)
        self.contract.save()
        self.assertIn(self.apartment, ContractForm(actor=self.manager).fields['apartment'].queryset)

    def test_invalid_dates_render_normally(self):
        form = ContractForm(data={'start_date': 'invalid', 'end_date': ''}, actor=self.manager)
        self.assertFalse(form.is_valid())
        self.assertIn(self.free, form.fields['apartment'].queryset)
