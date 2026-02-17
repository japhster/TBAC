from django.contrib.auth.models import User
from django.shortcuts import reverse

from tbac.tests import BaseLoggedInTestCase
from tbac import models

# Create your tests here.


class CreateRoomTestCase(BaseLoggedInTestCase):
    def setUp(self):
        super().setUp()

        self.game = models.Game.objects.create(name="Test Game", created_by=self.user)

        self.room_data = {
            "name": "Test Room",
            "description": "A Room",
            "visited_description": "A visited room",
        }

    def test_create_room(self):
        response = self.client.post(
            reverse("room:new", kwargs={"game_pk": self.game.pk}), self.room_data
        )
        self.assertEqual(response.status_code, 302)

        room = models.Room.objects.get()
        for field, expected_value in self.room_data.items():
            with self.subTest(field=field, expected_value=expected_value):
                self.assertEqual(getattr(room, field), expected_value)

        self.assertEqual(room.game, self.game)

    def test_visited_description_is_not_required(self):
        del self.room_data["visited_description"]

        response = self.client.post(
            reverse("room:new", kwargs={"game_pk": self.game.pk}), self.room_data
        )
        self.assertEqual(response.status_code, 302)

        room = models.Room.objects.get()
        for field, expected_value in self.room_data.items():
            with self.subTest(field=field, expected_value=expected_value):
                self.assertEqual(getattr(room, field), expected_value)

        self.assertEqual(room.game, self.game)
        self.assertEqual(room.visited_description, "")


    def test_create_room_with_required_items(self):
        existing_room = models.Room.objects.create(
            name="Room with Item", game=self.game
        )
        item = models.Item.objects.create(
            name="Key", room=existing_room, game=self.game
        )

        response = self.client.post(
            reverse("room:new", kwargs={"game_pk": self.game.pk}),
            {**self.room_data, "required_items": [item.pk]},
        )
        self.assertEqual(response.status_code, 302)

        room = models.Room.objects.exclude(pk=existing_room.pk).get()
        for field, expected_value in self.room_data.items():
            with self.subTest(field=field, expected_value=expected_value):
                self.assertEqual(getattr(room, field), expected_value)

        self.assertEqual(room.game, self.game)
        self.assertEqual(room.required_items.count(), 1)
        self.assertEqual(room.required_items.first(), item)

    def test_cannot_create_room_for_game_created_by_another(self):
        self.game.created_by = User.objects.create(email="another@person.com")
        self.game.save()

        response = self.client.post(
            reverse("room:new", kwargs={"game_pk": self.game.pk}), self.room_data
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(models.Room.objects.exists())


class SetAsStartingRoomTestCase(BaseLoggedInTestCase):
    def setUp(self):
        super().setUp()
        self.game = models.Game.objects.create(name="Test Game", created_by=self.user)
        self.room = models.Room.objects.create(name="Test Room", game=self.game)

    def test_set_as_starting_room(self):
        response = self.client.get(
            reverse("room:set_starting", kwargs={"room_pk": self.room.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.start_room, self.room)

    def test_cannot_set_starting_room_on_game_not_created_by_self(self):
        self.game.created_by = User.objects.create(email="another@person.com")
        self.game.save()

        response = self.client.get(
            reverse("room:set_starting", kwargs={"room_pk": self.room.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_overwrites_existing_start_room(self):
        self.game.start_room = models.Room.objects.create(name="Start Room", game=self.game)
        self.game.save()

        response = self.client.get(
            reverse("room:set_starting", kwargs={"room_pk": self.room.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.start_room, self.room)