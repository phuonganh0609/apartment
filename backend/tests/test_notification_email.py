from unittest.mock import patch
import smtplib

from django.core import mail
from django.core.cache import cache
from django.test import override_settings

from accounts.models import AuditEvent
from payments.models import Payment
from .base import DomainTestCase


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NotificationEmailTests(DomainTestCase):
    def setUp(self):
        cache.clear()
        self.client.force_login(self.manager)
        self.url = f'/ai/contracts/{self.contract.pk}/notification/'

    def draft(self, payment=None):
        with patch('ai_assistant.views.generate_notification', return_value={
            'subject': 'Nhắc gia hạn', 'body': 'Nội dung bản nháp',
        }):
            response = self.client.post(self.url, {'payment': payment} if payment else {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gửi email')
        form = response.context['email_form']
        self.assertEqual(form.initial['recipient'], self.tenant.email)
        data = dict(form.initial, action='send', subject='Tiêu đề đã sửa', body='Nội dung đã sửa')
        if payment:
            data['payment'] = payment
        return data

    def test_send_edited_email_once_and_audit(self):
        data = self.draft()
        with patch('ai_assistant.views.generate_notification') as generate:
            response = self.client.post(self.url, data)
            generate.assert_not_called()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.tenant.email])
        self.assertEqual(mail.outbox[0].subject, 'Tiêu đề đã sửa')
        self.assertEqual(mail.outbox[0].body, 'Nội dung đã sửa')
        self.assertTrue(AuditEvent.objects.filter(action='notification_email_sent').exists())
        self.client.post(self.url, data)
        self.assertEqual(len(mail.outbox), 1)

    def test_invalid_email_and_header_injection_rejected(self):
        data = self.draft()
        for field, value in [('recipient', 'invalid'), ('subject', 'Hello\r\nBcc: other@example.com')]:
            response = self.client.post(self.url, dict(data, **{field: value}))
            self.assertTrue(response.context['email_form'].errors)
        self.assertEqual(len(mail.outbox), 0)

    def test_smtp_error_preserves_edits_and_allows_retry(self):
        data = self.draft()
        with patch('ai_assistant.views.EmailMessage.send', side_effect=smtplib.SMTPException('private failure')):
            response = self.client.post(self.url, data)
        self.assertContains(response, 'Chưa xác nhận gửi email thành công')
        self.assertEqual(response.context['email_form']['body'].value(), data['body'])
        self.assertEqual(self.client.post(self.url, data).status_code, 302)

    def test_assignment_and_role_checked_again_when_sending(self):
        data = self.draft()
        self.contract.ai_authorized_users.remove(self.manager)
        self.assertEqual(self.client.post(self.url, data).status_code, 404)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(self.url, data).status_code, 403)
        self.assertEqual(len(mail.outbox), 0)

    def test_payment_context_cannot_be_changed(self):
        payment = Payment.objects.create(contract=self.contract, kind='rent', amount=5000000,
            due_date=self.today, status='pending')
        data = self.draft(payment.pk)
        data.pop('payment')
        self.assertEqual(self.client.post(self.url, data).status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        data['payment'] = payment.pk
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_forged_draft_cannot_send(self):
        response = self.client.post(self.url, {
            'action': 'send', 'recipient': 'test@example.com', 'subject': 'Test',
            'body': 'Test', 'draft_token': 'forged',
        })
        self.assertTrue(response.context['email_form'].non_field_errors())
        self.assertEqual(len(mail.outbox), 0)
