from django.core.cache import cache
from django.test import Client
from django.urls import reverse
from .base import DomainTestCase


class AuthTests(DomainTestCase):
    def test_anonymous_redirected(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_login_and_logout_post_only(self):
        self.assertTrue(
            self.client.login(username="staff", password="Test-Password-2026!")
        )
        self.assertEqual(self.client.get("/accounts/logout/").status_code, 405)
        self.assertEqual(
            self.client.post("/accounts/logout/").status_code, 302
        )

    def test_staff_cannot_access_financial_pages(self):
        self.client.force_login(self.staff)
        for url in [
            "/payments/",
            "/payments/new/",
            "/payments/debts/",
            "/reports/revenue/",
            "/reports/debts/",
            "/reports/occupancy/",
            "/accounts/users/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        response = self.client.get("/")
        self.assertNotContains(response, "Doanh thu tháng")
        self.assertNotContains(response, "Công nợ hiện tại")

    def test_accountant_read_but_not_edit_contracts(self):
        self.client.force_login(self.accountant)
        self.assertEqual(self.client.get("/contracts/").status_code, 200)
        for suffix in ["edit/", "extend/", "terminate/"]:
            self.assertEqual(
                self.client.post(
                    f"/contracts/{self.contract.pk}/{suffix}", {}
                ).status_code,
                403,
            )
        self.assertEqual(
            self.client.get(
                f"/ai/contracts/{self.contract.pk}/summary/"
            ).status_code,
            403,
        )
        self.assertEqual(self.client.get("/maintenance/").status_code, 403)

    def test_deposit_update_cannot_change_contract(self):
        self.client.force_login(self.accountant)
        response = self.client.post(
            f"/contracts/{self.contract.pk}/deposit/",
            {
                "deposit_amount": "12000000",
                "code": "HACKED",
                "status": "terminated",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.deposit_amount, 12000000)
        self.assertEqual(self.contract.code, "TEST-001")
        self.assertEqual(self.contract.status, "active")

    def test_staff_has_no_implicit_deposit_edit(self):
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.post(
                f"/contracts/{self.contract.pk}/deposit/",
                {"deposit_amount": 0},
            ).status_code,
            403,
        )

    def test_account_create_cannot_grant_superuser(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            "/accounts/users/new/",
            {
                "username": "newstaff",
                "full_name": "New staff",
                "role": "staff",
                "is_active": "on",
                "new_password": "Safe-password-3912!",
                "is_superuser": "on",
                "is_staff": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        from accounts.models import User

        user = User.objects.get(username="newstaff")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("Safe-password-3912!"))

    def test_manager_cannot_disable_self(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            f"/accounts/users/{self.manager.pk}/edit/",
            {"username": "manager", "full_name": "Manager", "role": "staff"},
        )
        self.assertEqual(response.status_code, 200)
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.is_active)
        self.assertEqual(self.manager.role, "manager")

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.manager)
        self.assertEqual(
            client.post("/buildings/new/", {"name": "CSRF"}).status_code, 403
        )

    def test_template_escapes_untrusted_content(self):
        self.tenant.full_name = "<script>alert(1)</script>"
        self.tenant.save()
        self.client.force_login(self.manager)
        response = self.client.get(f"/tenants/{self.tenant.pk}/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_inactive_account_rejected(self):
        self.staff.is_active = False
        self.staff.save()
        self.assertFalse(
            self.client.login(username="staff", password="Test-Password-2026!")
        )
