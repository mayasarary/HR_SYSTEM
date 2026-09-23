from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='employee', password='test-password-123'
        )

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'Sign in to your workspace')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_dashboard_requires_login(self):
        self.assertRedirects(self.client.get('/base/'), '/login/?next=/base/')

    def test_successful_login_and_logout(self):
        response = self.client.post('/login/', {
            'username': 'employee', 'password': 'test-password-123',
        })
        self.assertRedirects(response, '/base/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.assertRedirects(self.client.post('/logout/'), '/login/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_credentials(self):
        response = self.client.post('/login/', {
            'username': 'employee', 'password': 'wrong',
        })
        self.assertContains(response, 'Please enter a correct username and password')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_account_cannot_login(self):
        self.user.is_active = False
        self.user.save()
        self.client.post('/login/', {
            'username': 'employee', 'password': 'test-password-123',
        })
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_external_redirect_is_rejected(self):
        response = self.client.post('/login/', {
            'username': 'employee', 'password': 'test-password-123',
            'next': 'https://example.com/',
        })
        self.assertRedirects(response, '/base/')

    def test_authenticated_user_skips_login(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get('/login/'), '/base/')

    def test_login_requires_csrf(self):
        response = Client(enforce_csrf_checks=True).post('/login/', {
            'username': 'employee', 'password': 'test-password-123',
        })
        self.assertEqual(response.status_code, 403)
