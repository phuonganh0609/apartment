from datetime import timedelta
from django.test import override_settings
from alerts.services import expiring_contracts, overdue_payments
from payments.models import Payment
from .base import DomainTestCase


class AlertTests(DomainTestCase):
    @override_settings(EXPIRY_WARNING_DAYS=30)
    def test_expiry_boundaries(self):
        for days, included in [
            (-1, False),
            (0, True),
            (30, True),
            (31, False),
        ]:
            self.contract.end_date = self.today + timedelta(days=days)
            self.contract.save()
            self.assertEqual(
                expiring_contracts().filter(pk=self.contract.pk).exists(),
                included,
            )

    def test_due_today_not_overdue(self):
        payment = Payment.objects.create(
            contract=self.contract,
            amount=100,
            kind="rent",
            due_date=self.today,
        )
        self.assertFalse(overdue_payments().exists())
        payment.due_date -= timedelta(days=1)
        payment.save()
        self.assertTrue(overdue_payments().exists())
        payment.status = "paid"
        payment.paid_date = self.today
        payment.save()
        self.assertFalse(overdue_payments().exists())

    def test_staff_alerts_do_not_leak_amounts(self):
        Payment.objects.create(
            contract=self.contract,
            amount=9876543,
            kind="rent",
            due_date=self.today - timedelta(days=1),
        )
        self.client.force_login(self.staff)
        response = self.client.get("/alerts/")
        self.assertNotContains(response, "9876543")
        self.assertNotContains(response, "Thanh toán quá hạn")
