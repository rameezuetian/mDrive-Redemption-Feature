from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Customer


class AuthTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            membership_level='silver',
        )
        self.customer.set_password('secret123')
        self.customer.save()

    def test_signup_creates_customer(self):
        response = self.client.post(
            reverse('signup'),
            {
                'name': 'New User',
                'email': 'new@example.com',
                'phone': '0987654321',
                'password': 'newpassword123',
                'membership_level': 'silver',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Customer.objects.filter(email='new@example.com').exists())

    def test_login_returns_success_for_valid_credentials(self):
        response = self.client.post(
            reverse('login'),
            {'email': 'test@example.com', 'password': 'secret123'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@example.com')
