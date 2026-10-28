import re
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from .base import DomainTestCase


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(DomainTestCase):
    def setUp(self):
        cache.clear()
        self.manager.email = 'manager@example.com'
        self.manager.save()

    def test_email_link_changes_password_once(self):
        response = self.client.post('/accounts/password-reset/', {'email': self.manager.email})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r'http://testserver(/accounts/reset/\S+)', mail.outbox[0].body).group(1)
        page = self.client.get(link, follow=True)
        self.assertTrue(page.context['validlink'])
        result = self.client.post(page.request['PATH_INFO'], {
            'new_password1': 'New-Safe-Password-391!',
            'new_password2': 'New-Safe-Password-391!',
        })
        self.assertEqual(result.status_code, 302)
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.check_password('New-Safe-Password-391!'))
        self.assertFalse(self.client.get(link, follow=True).context['validlink'])

    def test_unknown_email_has_same_response_and_no_mail(self):
        result = self.client.post('/accounts/password-reset/', {'email': 'unknown@example.com'})
        self.assertEqual(result.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_expired_link_rejected(self):
        self.client.post('/accounts/password-reset/', {'email': self.manager.email})
        link = re.search(r'http://testserver(/accounts/reset/\S+)', mail.outbox[0].body).group(1)
        with override_settings(PASSWORD_RESET_TIMEOUT=-1):
            self.assertFalse(self.client.get(link, follow=True).context['validlink'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend', EMAIL_HOST='')
    def test_missing_smtp_has_actionable_message(self):
        result = self.client.post('/accounts/password-reset/', {'email': self.manager.email})
        self.assertContains(result, 'Chức năng gửi email chưa được cấu hình')
