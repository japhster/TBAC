from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.shortcuts import reverse


class BaseLoggedInTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email="test@person.com", password="Test123", username="test"
        )
        self.client = Client()
        self.client.force_login(self.user)
