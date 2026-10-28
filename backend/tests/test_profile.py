from .base import DomainTestCase


class ProfileTests(DomainTestCase):
    def test_profile_requires_login(self):
        self.assertEqual(self.client.get('/accounts/profile/').status_code, 302)

    def test_password_change_preserves_session(self):
        self.client.force_login(self.manager)
        self.assertContains(self.client.get('/accounts/profile/'), self.manager.username)
        result = self.client.post('/accounts/password/', {
            'old_password': 'Test-Password-2026!',
            'new_password1': 'New-Password-9264!',
            'new_password2': 'New-Password-9264!',
        })
        self.assertRedirects(result, '/accounts/profile/')
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.check_password('New-Password-9264!'))
        self.assertEqual(self.client.get('/dashboard/').status_code, 200)

    def test_manager_report_center(self):
        self.client.force_login(self.manager)
        self.assertContains(self.client.get('/reports/'), 'Công suất thuê')
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/reports/').status_code, 403)
