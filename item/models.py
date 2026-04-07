from django.db import models
import re

from tbac import mixins

# Create your models here.


class Item(mixins.SearchableMixin):
    class ItemTypeChoices(models.TextChoices):
        GENERIC = ("GENERIC", "Generic Item")
        KEY = ("KEY", "Key")
        CONTAINER = ("CONTAINER", "Container")
        LIGHT = ("LIGHT", "Light Source")

    description = models.CharField(max_length=1000)
    in_room_description = models.CharField(max_length=1000)
    item_type = models.CharField(max_length=20, choices=ItemTypeChoices.choices)
    game = models.ForeignKey(
        "game.Game", related_name="items", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "room.Room", related_name="items", on_delete=models.SET_NULL, null=True
    )
    can_be_taken = models.BooleanField(default=True)
    contained_within = models.ForeignKey(
        "self",
        related_name="contents",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    is_starting_item = models.BooleanField(default=False)
    # specific details for containers
    container_is_locked = models.BooleanField(default=False)
    container_key_required = models.ForeignKey(
        "self",
        related_name="unlocks_containers",
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to=models.Q(item_type=ItemTypeChoices.KEY),
    )
    container_discard_after_open = models.BooleanField(default=True)
    container_open_name = models.CharField(max_length=250, blank=True)

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="items",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    in_inventory = models.BooleanField(default=False)
    container_is_open = models.BooleanField(default=False)

    objects = mixins.SessionManager()

    def __str__(self):
        if self.container_is_open and self.container_open_name:
            return self.container_open_name

        return self.name


class Puzzle(models.Model):
    """
    A puzzle with a specific answer
    e.g.
     - a multi-digit code
     - a riddle
     - an anagram
    """

    name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    solution = models.CharField(max_length=250)
    game = models.ForeignKey(
        "game.Game", related_name="puzzles", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "room.Room", related_name="puzzles", on_delete=models.CASCADE
    )
    solved_name = models.CharField(max_length=250)
    solved_description = models.CharField(max_length=1000)

    # session tracking
    session = models.ForeignKey(
        "game.Session", related_name="puzzles", on_delete=models.CASCADE
    )
    is_solved = models.BooleanField(default=False)

    def solve(self, attempt):
        if attempt == solution:
            self.is_solved = True
            self.save()
            return True

        return False

    def get_description(self):
        if self.is_solved and self.solved_description:
            return self.solved_description

        return self.description

    def __str__(self):
        if self.is_solved and self.solved_name:
            return self.sovled_name

        return self.name
