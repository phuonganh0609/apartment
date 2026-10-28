from datetime import timedelta
from payments.models import Payment
from alerts.services import upcoming_payments
from .base import DomainTestCase


class AccountingUITests(DomainTestCase):
    def test_upcoming_boundaries(self):
        for offset in (-1, 0, 7, 8):
            Payment.objects.create(contract=self.contract, kind='rent', amount=100,
                                   due_date=self.today + timedelta(days=offset))
        self.assertEqual(list(upcoming_payments().values_list('due_date', flat=True)),
                         [self.today, self.today + timedelta(days=7)])

    def test_debt_search_and_overdue_filter(self):
        Payment.objects.create(contract=self.contract, kind='rent', amount=100,
                               due_date=self.today - timedelta(days=1))
        self.client.force_login(self.accountant)
        page = self.client.get('/payments/debts/', {'q': self.apartment.code, 'overdue': '1'})
        self.assertEqual(page.context['page_obj'].paginator.count, 1)
        page = self.client.get('/payments/debts/', {'q': 'DOES-NOT-EXIST'})
        self.assertEqual(page.context['page_obj'].paginator.count, 0)

    def test_deposit_status_update_and_menu(self):
        self.client.force_login(self.accountant)
        self.assertContains(self.client.get('/'), 'Tổng quan tài chính')
        result = self.client.post(f'/contracts/{self.contract.pk}/deposit/',
                                 {'deposit_amount': 1000, 'deposit_status': 'collected'})
        self.assertEqual(result.status_code, 302)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.deposit_status, 'collected')
