from django.test import Client
from accounts.models import User, AuditEvent
from maintenance.models import MaintenanceRequest
from .base import DomainTestCase


class AccountDeletionTests(DomainTestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='Test-admin-2026!')
        self.target = User.objects.create_user(username='resident', role='tenant', tenant=self.tenant)
        self.url = f'/accounts/users/{self.target.pk}/delete/'

    def test_only_admin_can_see_action_and_delete(self):
        for account in (self.manager, self.staff, self.accountant, self.target):
            self.client.force_login(account)
            for method in (self.client.get, self.client.post):
                self.assertEqual(method(self.url).status_code, 403)
        self.client.force_login(self.manager)
        detail = self.client.get(f'/accounts/users/{self.target.pk}/')
        self.assertNotContains(detail, self.url)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(f'/accounts/users/{self.target.pk}/'), self.url)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertTrue(User.objects.filter(pk=self.target.pk).exists())

    def test_delete_preserves_business_data_and_logs_actor(self):
        ticket = MaintenanceRequest.objects.create(apartment=self.apartment, submitted_by=self.target, content='Test')
        self.client.force_login(self.admin)
        self.assertRedirects(self.client.post(self.url), '/accounts/users/')
        self.assertFalse(User.objects.filter(pk=self.target.pk).exists())
        self.tenant.refresh_from_db()
        self.contract.refresh_from_db()
        ticket.refresh_from_db()
        self.assertIsNone(ticket.submitted_by_id)
        self.assertEqual(self.contract.tenant_id, self.tenant.pk)
        self.assertTrue(AuditEvent.objects.filter(actor='admin', action='account_deleted').exists())

    def test_cannot_delete_self(self):
        self.client.force_login(self.admin)
        url = f'/accounts/users/{self.admin.pk}/delete/'
        self.assertNotContains(self.client.get(f'/accounts/users/{self.admin.pk}/'), url)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_requires_login_and_csrf(self):
        self.assertEqual(self.client.post(self.url).status_code, 302)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        self.assertEqual(client.post(self.url).status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.target.pk).exists())
