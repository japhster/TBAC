from django.contrib.auth.models import User
from django.shortcuts import reverse

from tbac.tests import BaseLoggedInTestCase
from tbac import models

# Create your tests here.


class CreateItemTestCase(BaseLoggedInTestCase):
    def setUp(self):
        super().setUp()

        self.room = models.Room.objects.create(name="A Room", game=self.game)

        self.item_data = {
            "name": "Test Item",
            "description": "An item",
            "item_type": "KEY",
            "room": self.room.pk,
        }

    def test_create_item(self):
        response = self.client.post(
            reverse("item:new", kwargs={"game_pk": self.game.pk}), self.item_data
        )
        self.assertEqual(response.status_code, 302)

        item = models.Item.objects.get()
        del self.item_data["room"]
        for field, expected_value in self.item_data.items():
            with self.subTest(field=field, expected_value=expected_value):
                self.assertEqual(getattr(item, field), expected_value)

        self.assertEqual(item.game, self.game)
        self.assertEqual(item.room, self.room)

    def test_create_item_inside_container(self):
        del self.item_data["room"]
        container = models.Item.objects.create(
            name="Container",
            item_type=models.Item.ItemTypeChoices.CONTAINER,
            game=self.game,
            room=self.room,
        )

        response = self.client.post(
            reverse("item:new", kwargs={"game_pk": self.game.pk}),
            {**self.item_data, "contained_within": container.pk},
        )
        self.assertEqual(response.status_code, 302)

        item = models.Item.objects.last()
        for field, expected_value in self.item_data.items():
            with self.subTest(field=field, expected_value=expected_value):
                self.assertEqual(getattr(item, field), expected_value)

        self.assertEqual(item.game, self.game)
        self.assertEqual(item.contained_within, container)
        self.assertIsNone(item.room)

    def test_create_starting_item(self):
        del self.item_data["room"]
        response = self.client.post(
            reverse("item:new", kwargs={"game_pk": self.game.pk}),
            {**self.item_data, "is_starting_item": True},
        )
        self.assertEqual(response.status_code, 302)

        item = models.Item.objects.get()
        for field, expected_value in self.item_data.items():
            with self.subTest(field=field, expected_value=expected_value):
                self.assertEqual(getattr(item, field), expected_value)

        self.assertEqual(item.game, self.game)
        self.assertTrue(item.is_starting_item)
        self.assertIsNone(item.room)
