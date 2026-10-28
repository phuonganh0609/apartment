from django.core.cache import cache
from accounts.models import User
from .base import DomainTestCase


class RegistrationTests(DomainTestCase):
    def setUp(self):
        cache.clear()
        self.data = {'username': 'newtenant', 'full_name': 'New Tenant',
                     'email': 'newtenant@example.com',
                     'password1': 'Safe-New-Password-426!', 'password2': 'Safe-New-Password-426!'}

    def test_registration_cannot_escalate_or_link_private_profile(self):
        self.data.update(role='manager', is_superuser='on', is_staff='on',
                         can_edit_deposit='on', tenant=self.tenant.pk)
        result = self.client.post('/register/', self.data)
        self.assertEqual(result.status_code, 302)
        user = User.objects.get(username='newtenant')
        self.assertEqual(user.role, 'tenant')
        self.assertIsNone(user.tenant_id)
        self.assertFalse(user.is_staff or user.is_superuser or user.can_edit_deposit)
        self.assertTrue(self.client.login(username='newtenant', password=self.data['password1']))
        self.assertNotContains(self.client.get('/my-home/'), self.contract.code)
        self.assertEqual(self.client.get('/payments/').status_code, 403)

    def test_duplicate_email_and_weak_password_rejected(self):
        self.manager.email = 'newtenant@example.com'
        self.manager.save()
        self.assertEqual(self.client.post('/register/', self.data).status_code, 200)
        self.assertFalse(User.objects.filter(username='newtenant').exists())
        self.data.update(email='other@example.com', password1='123', password2='123')
        self.assertEqual(self.client.post('/register/', self.data).status_code, 200)
        self.assertFalse(User.objects.filter(username='newtenant').exists())
