from django.conf import settings
from django.db import models

from item.models import Item
from room.models import Exit
from tbac import mixins

import random

# Create your models here.


class GameManager(models.Manager):

    def playable(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        qs = self.filter(*args, **kwargs)
        if user:
            qs = qs.filter(models.Q(is_published=True) | models.Q(sessions__user=user))
        if "start_room" not in kwargs:
            qs = qs.filter(start_room__isnull=False)

        if "created_by" not in kwargs:
            qs = qs.filter(created_by__isnull=False)

        return qs


class Game(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=1000)
    starting_health = models.IntegerField(default=100)
    base_damage = models.OneToOneField("DamageOutput", on_delete=models.CASCADE)
    start_room = models.OneToOneField(
        "room.Room", related_name="starts_game", null=True, on_delete=models.SET_NULL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="games",
        null=True,
        on_delete=models.SET_NULL,
    )
    is_published = models.BooleanField(default=False)

    objects = GameManager()

    def __str__(self):
        return self.name


class EndState(models.Model):
    """A Set of conditions that all must be true to reach an Ending in a Game
    EndState.is_success defines if the End State is a Win or Loss.
    """

    is_success = models.BooleanField(default=True)
    name = models.CharField(max_length=250)
    message = models.CharField(max_length=1000)
    game = models.ForeignKey(
        "Game", related_name="end_states", on_delete=models.CASCADE
    )
    session = models.ForeignKey(
        "Session",
        related_name="end_states",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    owned_items = models.ManyToManyField("item.Item", related_name="+")
    location = models.ForeignKey(
        "room.Room", related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = mixins.SessionManager()

    def end_state_met(self):
        return all(self.owned_items.all().values_list("in_inventory", flat=True)) and (
            self.location is None or self.session.current_location == self.location
        )


class Player(models.Model):
    name = models.CharField(max_length=250)
    session = models.OneToOneField(
        "Session", related_name="player", on_delete=models.CASCADE
    )
    health = models.IntegerField()
    base_damage = models.OneToOneField("DamageOutput", on_delete=models.CASCADE)

    current_health = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Session(models.Model):
    game = models.ForeignKey("Game", related_name="sessions", on_delete=models.CASCADE)
    current_location = models.ForeignKey(
        "room.Room",
        related_name="+",
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(session__isnull=False),
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sessions", on_delete=models.CASCADE
    )

    def get_inventory(self):
        return self.items.all().filter(in_inventory=True)

    def get_openable_containers(self):
        return self.get_inventory().filter(
            item_type=Item.ItemTypeChoices.CONTAINER, container_is_open=False
        )

    def get_available_rooms(self):
        exits = (
            Exit.objects.filter(
                models.Q(room_1=self.current_location)
                | models.Q(room_2=self.current_location),
            )
            .select_related("room_1", "room_2")
            .prefetch_related("room_1__required_items", "room_2__required_items")
        )

        current_inventory = self.get_inventory()

        available_rooms = []

        for location_exit in exits:
            if location_exit.is_locked:
                continue
            moving_to = (
                location_exit.room_2
                if self.current_location == location_exit.room_1
                else location_exit.room_1
            )

            if moving_to.required_items.exists() and any(
                not item.in_inventory for item in moving_to.required_items.all()
            ):
                continue

            available_rooms.append(moving_to)

        return available_rooms

    def get_exits(self):
        return (
            Exit.objects.filter(
                models.Q(room_1=self.current_location)
                | models.Q(room_2=self.current_location),
            )
            .select_related("room_1", "room_2")
            .prefetch_related("room_1__required_items", "room_2__required_items")
        )


class TriggerableEffect(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)

    game = models.ForeignKey(
        "game.Game", related_name="triggerable_effects", on_delete=models.CASCADE
    )
    is_starting_quest = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    # tasks
    room_entered = models.ForeignKey(
        "room.Room",
        related_name="effects_upon_entry",
        on_delete=models.CASCADE,
        null=True,
    )
    items_owned = models.ManyToManyField(
        "item.Item", related_name="effects_upon_acquisition"
    )
    item_used = models.ForeignKey(
        "item.Item",
        related_name="effects_upon_use",
        on_delete=models.CASCADE,
        null=True,
    )
    puzzles_solved = models.ManyToManyField(
        "item.Puzzle", related_name="effects_upon_solving"
    )

    # rewards
    items_gained = models.ManyToManyField("item.Item", related_name="gained_through")
    exits_unlocked = models.ManyToManyField("room.Exit", related_name="unlocked_by")
    effects_accepted = models.ManyToManyField(
        "TriggerableEffect", related_name="triggered_by"
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session", related_name="triggerable_effects", on_delete=models.CASCADE
    )
    is_accepted = models.BooleanField(default=False)
    is_achieved = models.BooleanField(default=False)

    def complete(self):
        if (
            self.is_accepted
            and not self.is_achieved
            and self.room_entered == self.session.current_location
            and all(item.in_inventory for item in self.items_owned.all())
            and all(puzzle.is_solved for puzzle in self.puzzles_solved.all())
        ):
            self.items_gained.update(in_inventory=True)
            self.exits_unlocked.update(is_locked=False)
            self.effects_nullified.update(is_nullified=False)
            self.is_triggered = True
            self.save()
            return True

        return False

    def trigger_effects(self):
        self.items_gained.update(in_inventory=True)
        self.exits_unlocked.update(is_locked=False)
        self.effects_accepted.all().update(is_accepted=True)


class DamageOutput(models.Model):
    min_damage = models.IntegerField()
    max_damage = models.IntegerField()

    def get_damage(self):
        return random.randint(self.min_damage, self.max_damage)

    def __str__(self):
        if self.min_damage == self.max_damage:
            return f"({self.min_damage})"
        return f"({self.min_damage} - {self.max_damage})"
