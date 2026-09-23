from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from contracts.models import Contract
from contracts.services import (
    extend_contract,
    save_contract,
    terminate_contract,
)
from buildings.services import apartments_with_occupancy
from .base import DomainTestCase


class ContractTests(DomainTestCase):
    def test_end_after_start(self):
        self.contract.end_date = self.contract.start_date
        with self.assertRaises(ValidationError):
            save_contract(self.contract)

    def test_overlapping_active_contract_rejected(self):
        duplicate = Contract(
            code="DUPLICATE",
            apartment=self.apartment,
            tenant=self.tenant,
            start_date=self.today,
            end_date=self.today + timedelta(days=50),
            status="active",
        )
        with self.assertRaises(ValidationError):
            save_contract(duplicate)

    def test_nonoverlapping_future_contract_allowed(self):
        future = Contract(
            code="FUTURE",
            apartment=self.apartment,
            tenant=self.tenant,
            start_date=self.contract.end_date + timedelta(days=1),
            end_date=self.contract.end_date + timedelta(days=100),
            status="active",
        )
        save_contract(future)
        self.assertIsNotNone(future.pk)

    def test_extension_cannot_overlap_future_booking(self):
        future = Contract(
            code="FUTURE",
            apartment=self.apartment,
            tenant=self.tenant,
            start_date=self.contract.end_date + timedelta(days=1),
            end_date=self.contract.end_date + timedelta(days=100),
            status="active",
        )
        save_contract(future)
        with self.assertRaises(ValidationError):
            extend_contract(self.contract.pk, future.end_date)

    def test_terminate_releases_occupancy_not_debt(self):
        from payments.models import Payment

        Payment.objects.create(
            contract=self.contract,
            amount=5000000,
            kind="rent",
            due_date=self.today,
        )
        self.assertTrue(
            apartments_with_occupancy().get(pk=self.apartment.pk).occupied_now
        )
        terminate_contract(self.contract.pk)
        self.assertFalse(
            apartments_with_occupancy().get(pk=self.apartment.pk).occupied_now
        )
        self.assertEqual(Payment.objects.get().debt, 5000000)

    def test_negative_deposit_db_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Contract.objects.filter(pk=self.contract.pk).update(
                deposit_amount=-1
            )

    def test_protected_apartment_cannot_be_deleted(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            f"/buildings/apartments/{self.apartment.pk}/delete/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "không thể xóa")

    def test_no_contract_delete_endpoint(self):
        self.client.force_login(self.manager)
        self.assertEqual(
            self.client.post(
                f"/contracts/{self.contract.pk}/delete/"
            ).status_code,
            404,
        )

    def test_maintenance_apartment_cannot_be_reserved(self):
        self.apartment.status = "maintenance"
        self.apartment.save()
        with self.assertRaises(ValidationError):
            save_contract(self.contract)
