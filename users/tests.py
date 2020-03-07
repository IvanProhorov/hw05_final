from django.test import TestCase, Client
from django.contrib.auth.models import User

# Create your tests here.
class TestRegistration(TestCase):
    def test_registration(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.client.login(username='sarah', password='12345')
        response = self.client.get("/sarah/")
        self.assertEqual(response.status_code, 200)