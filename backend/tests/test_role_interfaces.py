from accounts.models import User
from maintenance.models import MaintenanceRequest
from payments.models import Payment
from .base import DomainTestCase


class RoleInterfaceTests(DomainTestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer", role="tenant", tenant=self.tenant
        )

    def test_staff_menu_and_finance_denied(self):
        self.client.force_login(self.staff)
        page = self.client.get("/")
        self.assertContains(page, 'href="/maintenance/"')
        self.assertNotContains(page, 'href="/contracts/deposits/"')
        self.assertEqual(self.client.get("/contracts/deposits/").status_code, 403)
        self.assertEqual(self.client.post(f"/tenants/{self.tenant.pk}/delete/").status_code, 403)
        page = self.client.get(f"/tenants/{self.tenant.pk}/")
        self.assertNotContains(page, f'href="/tenants/{self.tenant.pk}/delete/"')

    def test_accountant_menu_and_operations_denied(self):
        self.client.force_login(self.accountant)
        page = self.client.get("/")
        self.assertContains(page, 'href="/contracts/deposits/"')
        for path in ("/buildings/", "/buildings/apartments/", "/tenants/", "/maintenance/"):
            self.assertNotContains(page, f'href="{path}"')
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_customer_denied_internal_pages_and_menu(self):
        self.client.force_login(self.customer)
        self.assertRedirects(self.client.get("/"), "/my-home/")
        page = self.client.get("/my-home/")
        for path in ("/contracts/", "/payments/", "/maintenance/", "/tenants/", "/accounts/users/", "/alerts/", "/regulations/"):
            self.assertNotContains(page, f'href="{path}"')
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_customer_cannot_select_other_apartment_or_set_status(self):
        from buildings.models import Apartment
        other = Apartment.objects.create(
            building=self.building, code="OTHER", floor=1, area=40, rent=1
        )
        self.client.force_login(self.customer)
        payload = {"apartment": other.pk, "content": "Repair", "priority": "normal"}
        self.assertEqual(self.client.post("/my-home/", payload).status_code, 200)
        self.assertFalse(MaintenanceRequest.objects.exists())
        payload.update(apartment=self.apartment.pk, status="done", notes="forged")
        self.assertEqual(self.client.post("/my-home/", payload).status_code, 302)
        item = MaintenanceRequest.objects.get()
        self.assertEqual(item.status, "open")
        self.assertEqual(item.notes, "")
        self.assertEqual(item.submitted_by, self.customer)
        self.client.force_login(self.staff)
        self.assertContains(self.client.get("/maintenance/"), "Repair")

    def test_customer_without_link_sees_no_private_data(self):
        MaintenanceRequest.objects.create(apartment=self.apartment, content="PRIVATE-REPAIR")
        self.customer.tenant = None
        self.customer.save()
        self.client.force_login(self.customer)
        page = self.client.get("/my-home/")
        self.assertNotContains(page, self.contract.code)
        self.assertNotContains(page, "PRIVATE-REPAIR")
        self.assertEqual(len(page.context["form"].fields["apartment"].queryset), 0)
