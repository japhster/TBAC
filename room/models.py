from django.db import models
import re

from tbac import mixins

# Create your models here.


class ExitManager(mixins.SessionManager):
    def from_room(self, *args, **kwargs):
        room = kwargs.pop("room")
        return self.filter(*args, **kwargs).filter(
            models.Q(room_1=room) | models.Q(room_2=room)
        )


class Room(mixins.SearchableMixin):
    game = models.ForeignKey(
        "game.Game", related_name="rooms", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=1000)
    visited_description = models.CharField(max_length=1000, blank=True)
    exits = models.ManyToManyField("self", through="Exit")
    required_items = models.ManyToManyField(
        "item.Item", related_name="required_by_rooms"
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="rooms",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    visited = models.BooleanField(default=False)

    objects = mixins.SessionManager()

    def __str__(self):
        return self.name


class Exit(models.Model):
    room_1 = models.ForeignKey(
        "Room", related_name="exits_from_1", on_delete=models.CASCADE
    )
    room_2 = models.ForeignKey(
        "Room", related_name="exists_from_2", on_delete=models.CASCADE
    )
    is_locked = models.BooleanField(default=False)
    key_required = models.ForeignKey(
        "item.Item", related_name="unlocks", on_delete=models.SET_NULL, null=True
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="exits",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )

    objects = ExitManager()

    def get_exit_room(self, room):
        return self.room_2 if room == self.room_1 else self.room_1

    def __str__(self):
        return f"Exit between {self.room_1.name} and {self.room_2.name}."
