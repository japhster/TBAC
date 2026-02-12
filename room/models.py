from django.db import models

# Create your models here.


class ExitManager(models.Manager):
    def base(self):
        return self.get_queryset().filter(session__isnull=True)

    def session(self, session_pk):
        return self.get_queryset().filter(session_id=session_pk)

    def from_room(self, *args, **kwargs):
        room = kwargs.pop("room")
        return self.filter(*args, **kwargs).filter(
            models.Q(room_1=room) | models.Q(room_2=room)
        )


class RoomManager(models.Manager):
    def base(self):
        return self.get_queryset().filter(session__isnull=True)

    def session(self, session_pk):
        return self.get_queryset().filter(session_id=session_pk)


class Room(models.Model):
    game = models.ForeignKey(
        "game.Game", related_name="rooms", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=250)
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

    objects = RoomManager()

    def __str__(self):
        return self.name


class Exit(models.Model):
    room_1 = models.ForeignKey(
        "Room", related_name="exits_from_1", on_delete=models.CASCADE
    )
    room_2 = models.ForeignKey(
        "Room", related_name="exists_from_2", on_delete=models.CASCADE
    )
    one_to_two = models.CharField(max_length=250)
    two_to_one = models.CharField(max_length=250)
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

    def get_exit_name_and_room_pk(self, room):
        if room == self.room_1:
            return self.one_to_two, self.room_2.pk
        else:
            return self.two_to_one, self.room_1.pk

    def __str__(self):
        return f"Exit between {self.room_1.name} and {self.room_2.name}."
