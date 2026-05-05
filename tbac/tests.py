from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.shortcuts import reverse
from . import models


def create_game(user, name="Test Game 1", is_published=True):
    return models.Game.objects.create(
        name=name,
        created_by=user,
        is_published=is_published,
        base_damage=models.DamageOutput.objects.create(min_damage=10, max_damage=10),
    )


class BaseLoggedInTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email="test@person.com", password="Test123", username="test"
        )
        self.client = Client()
        self.client.force_login(self.user)

        self.game = create_game(self.user)
