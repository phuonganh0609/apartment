from accounts.models import User
from .base import DomainTestCase


class AdminPortalTests(DomainTestCase):
    def test_only_superuser_can_open_admin(self):
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        for user in (self.manager, self.staff, self.accountant):
            self.client.force_login(user)
            self.assertEqual(self.client.get('/admin/').status_code, 403)
        admin = User.objects.create_superuser(username='testadmin', password='Safe-password-492!')
        self.client.force_login(admin)
        self.assertContains(self.client.get('/admin/'), 'Quản trị hệ thống')
        for path in ('roles', 'data', 'settings', 'logs', 'backups'):
            self.assertEqual(self.client.get(f'/admin/{path}/').status_code, 200)

    def test_non_admin_cannot_read_or_change_settings(self):
        self.client.force_login(self.manager)
        for path in ('roles', 'data', 'settings', 'logs', 'backups'):
            self.assertEqual(self.client.get(f'/admin/{path}/').status_code, 403)
            self.assertEqual(self.client.post(f'/admin/{path}/', {}).status_code, 403)

    def test_settings_and_account_changes_are_logged(self):
        from accounts.models import SystemSettings, AuditEvent
        admin = User.objects.create_superuser(username='testadmin', password='Safe-password-492!')
        self.client.force_login(admin)
        response = self.client.post('/admin/settings/', {'contact_phone':'0900000000', 'contact_email':'public@example.com', 'expiry_warning_days':14})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SystemSettings.objects.get(pk=1).expiry_warning_days, 14)
        self.assertContains(self.client.get('/contact/'), 'public@example.com')
        self.assertTrue(AuditEvent.objects.filter(actor='testadmin', action='Lưu cấu hình hệ thống').exists())
        self.staff.is_active = False
        self.staff.save()
        self.assertTrue(AuditEvent.objects.filter(action='Cập nhật tài khoản', detail__contains='staff').exists())
