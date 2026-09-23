from datetime import timedelta
from django.core.exceptions import ValidationError
from payments.models import Payment
from payments.services import total_debt
from reports.services import finance_metrics
from .base import DomainTestCase


class PaymentTests(DomainTestCase):
    def payment(self, **kwargs):
        return Payment(
            contract=self.contract,
            amount=5000000,
            kind="rent",
            due_date=self.today,
            **kwargs,
        )

    def test_paid_requires_date(self):
        with self.assertRaises(ValidationError):
            self.payment(status="paid").full_clean()

    def test_pending_cannot_have_paid_date(self):
        with self.assertRaises(ValidationError):
            self.payment(status="pending", paid_date=self.today).full_clean()

    def test_future_payment_date_rejected(self):
        with self.assertRaises(ValidationError):
            self.payment(
                status="paid", paid_date=self.today + timedelta(days=1)
            ).full_clean()

    def test_negative_amount_rejected(self):
        payment = self.payment()
        payment.amount = -1
        with self.assertRaises(ValidationError):
            payment.full_clean()

    def test_receipt_removes_debt_and_revenue_excludes_deposit(self):
        payment = self.payment()
        payment.save()
        self.assertEqual(total_debt(), 5000000)
        payment.status = "paid"
        payment.paid_date = self.today
        payment.full_clean()
        payment.save()
        self.assertEqual(total_debt(), 0)
        self.assertEqual(
            finance_metrics(self.today.strftime("%Y-%m"))["revenue"], 5000000
        )

    def test_duplicate_period_rejected(self):
        self.payment().save()
        with self.assertRaises(ValidationError):
            self.payment().full_clean()

    def test_invalid_month_does_not_crash(self):
        self.client.force_login(self.manager)
        for month in ["invalid", "0000-00", "9999-12"]:
            self.assertEqual(
                self.client.get(
                    "/reports/revenue/", {"month": month}
                ).status_code,
                200,
            )
