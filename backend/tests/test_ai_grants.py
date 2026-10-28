from accounts.models import User
from .base import DomainTestCase


class AIGrantTests(DomainTestCase):
    def test_assignment_required_for_internal_summary(self):
        for account in (self.manager, self.staff, self.accountant):
            self.client.force_login(account)
            self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/summary/').status_code, 200)
            self.contract.ai_authorized_users.remove(account)
            self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/summary/').status_code, 404)

    def test_tenant_only_own_summary_and_no_notification(self):
        account = User.objects.create_user(username='own', role='tenant', tenant=self.tenant)
        self.client.force_login(account)
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/summary/').status_code, 200)
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/notification/').status_code, 403)
        account.tenant = None
        account.save()
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/summary/').status_code, 404)

    def test_admin_needs_assignment_and_explicit_notice_grant(self):
        account = User.objects.create_superuser(username='aiadmin', password='Safe-Password-91!')
        self.client.force_login(account)
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/summary/').status_code, 404)
        self.contract.ai_authorized_users.add(account)
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/summary/').status_code, 200)
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/notification/').status_code, 403)
        account.can_ai_renewal_notice = True
        account.save()
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/notification/').status_code, 200)

    def test_accountant_renewal_requires_grant(self):
        self.client.force_login(self.accountant)
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/notification/').status_code, 403)
        self.accountant.can_ai_renewal_notice = True
        self.accountant.save()
        self.assertEqual(self.client.get(f'/ai/contracts/{self.contract.pk}/notification/').status_code, 200)
