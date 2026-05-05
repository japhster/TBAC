from django.contrib.auth.models import User
from django.shortcuts import reverse

from tbac.tests import BaseLoggedInTestCase, create_game
from tbac import models

# Create your tests here.


class GameListTestCase(BaseLoggedInTestCase):
    def setUp(self):
        super().setUp()

        self.game_2 = create_game(user=self.user, name="Test Game 2")

        self.game.rooms.create(name="Test Room")
        self.game.start_room = self.game.rooms.first()
        self.game.save()
        self.game_2.rooms.create(name="Test Room")
        self.game_2.start_room = self.game_2.rooms.first()
        self.game_2.save()

    def _test_num_games(self, num_games):
        response = self.client.get(reverse("game:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["games"]), num_games)

    def test_list(self):
        self._test_num_games(2)
        response = self.client.get(reverse("game:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["games"]), 2)

    def test_unpublished_games_not_in_list(self):
        self.game.is_published = False
        self.game.save()

        self._test_num_games(1)

    def test_unpublished_games_with_existing_session_in_list(self):
        self.game.is_published = False
        self.game.save()
        models.Session.objects.create(
            game=self.game,
            current_location=self.game.start_room,
            user=self.user,
        )

        self._test_num_games(2)

    def test_games_without_start_room_not_in_list(self):
        self.game.start_room = None
        self.game.save()

        self._test_num_games(1)

    def test_anonymous_games_not_in_list(self):
        self.game.created_by = None
        self.game.save()

        self._test_num_games(1)


class MyGamesTestCase(BaseLoggedInTestCase):
    def setUp(self):
        super().setUp()

        self.game_2 = create_game(user=self.user, name="Test Game 2")

    def _test_num_games(self, num_games):
        response = self.client.get(reverse("game:my_games"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["games"]), num_games)

    def test_my_games(self):
        self._test_num_games(2)

    def test_unowned_games_arent_included(self):
        self.game_2.created_by = None
        self.game_2.save()

        self._test_num_games(1)

        self.game_2.created_by = User.objects.create(email="another@user.com")
        self.game_2.save()

        self._test_num_games(1)
