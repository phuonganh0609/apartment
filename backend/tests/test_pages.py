from django.urls import reverse
from .base import DomainTestCase


class PageSmokeTests(DomainTestCase):
    def test_manager_pages_render(self):
        self.client.force_login(self.manager)
        paths = [
            "/",
            "/accounts/users/",
            "/accounts/users/new/",
            "/buildings/",
            "/buildings/new/",
            "/buildings/apartments/",
            "/buildings/apartments/new/",
            "/buildings/amenities/",
            "/buildings/apartment-amenities/",
            "/tenants/",
            "/tenants/new/",
            "/tenants/contacts/",
            "/contracts/",
            "/contracts/new/",
            "/contracts/deposits/",
            "/payments/",
            "/payments/new/",
            "/payments/debts/",
            "/maintenance/",
            "/maintenance/new/",
            "/alerts/",
            "/reports/revenue/",
            "/reports/occupancy/",
            "/reports/debts/",
            "/regulations/",
            "/regulations/new/",
            "/regulations/documents/new/",
            "/ai/chatbot/",
            f"/contracts/{self.contract.pk}/",
            f"/contracts/{self.contract.pk}/edit/",
            f"/contracts/{self.contract.pk}/extend/",
            f"/contracts/{self.contract.pk}/terminate/",
            f"/contracts/{self.contract.pk}/deposit/",
            f"/ai/contracts/{self.contract.pk}/summary/",
            f"/ai/contracts/{self.contract.pk}/notification/",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_invalid_filters_do_not_crash(self):
        self.client.force_login(self.manager)
        response = self.client.get(
            "/buildings/apartments/",
            {
                "building_id": "abc",
                "status": "bad",
                "page": "nonsense",
                "sort": "password",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_apartment_search(self):
        self.client.force_login(self.staff)
        self.assertContains(
            self.client.get("/buildings/apartments/", {"q": "A101"}), "A101"
        )
        self.assertNotContains(
            self.client.get("/buildings/apartments/", {"q": "NO_MATCH"}),
            "A101",
        )

    def test_empty_post_shows_validation_errors(self):
        self.client.force_login(self.manager)
        response = self.client.post("/tenants/new/", {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
