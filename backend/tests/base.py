from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from buildings.models import Apartment, Building
from contracts.models import Contract
from tenants.models import Tenant


class DomainTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.today = timezone.localdate()
        cls.manager = User.objects.create_user(
            username="manager",
            password="Test-Password-2026!",
            full_name="Manager",
            role="manager",
        )
        cls.staff = User.objects.create_user(
            username="staff",
            password="Test-Password-2026!",
            full_name="Staff",
            role="staff",
        )
        cls.accountant = User.objects.create_user(
            username="accountant",
            password="Test-Password-2026!",
            full_name="Accountant",
            role="accountant",
            can_edit_deposit=True,
        )
        cls.building = Building.objects.create(
            name="Test Building", address="Demo address"
        )
        cls.apartment = Apartment.objects.create(
            building=cls.building, code="A101", floor=1, area=45, rent=5000000
        )
        cls.tenant = Tenant.objects.create(
            full_name="Test Tenant",
            phone="0900000001",
            identity_number="000000000001",
            email="test@example.com",
            address="Private address",
        )
        cls.contract = Contract.objects.create(
            code="TEST-001",
            apartment=cls.apartment,
            tenant=cls.tenant,
            start_date=cls.today - timedelta(days=90),
            end_date=cls.today + timedelta(days=20),
            status="active",
            deposit_amount=10000000,
            contract_content=(
                "Thời hạn 12 tháng. Tiền thuê 5 triệu"
                " đồng mỗi tháng. Tiền cọc 10 triệu đ"
                "ồng."
            ),
        )
