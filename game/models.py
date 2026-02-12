from django.db import models

from item.models import Item
from room.models import Exit

# Create your models here.


class GameManager(models.Manager):

    def playable(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        if "start_room" not in kwargs:
            qs = qs.filter(start_room__isnull=False)

        return qs


class EndStateManager(models.Manager):
    def base(self):
        return self.get_queryset().filter(session__isnull=True)

    def session(self, session_pk):
        return self.get_queryset().filter(session_id=session_pk)


class Game(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=1000)
    start_room = models.OneToOneField(
        "room.Room", related_name="starts_game", null=True, on_delete=models.SET_NULL
    )

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

    objects = EndStateManager()

    def end_state_met(self):
        print(self.owned_items.all())

        return all(self.owned_items.all().values_list("in_inventory", flat=True)) and (
            self.location is None or self.session.current_location == self.location
        )


class Session(models.Model):
    game = models.ForeignKey("Game", related_name="sessions", on_delete=models.CASCADE)
    current_location = models.ForeignKey(
        "room.Room",
        related_name="+",
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(session__isnull=False),
        null=True,
    )

    def get_inventory(self):
        return self.items.all().filter(in_inventory=True)

    def get_openable_containers(self):
        return self.get_inventory().filter(
            item_type=Item.ItemTypeChoices.CONTAINER, container_is_open=False
        )

    def get_exit_names_and_room_pks(self):
        """Used in a session to generate the list of directions a player can go."""
        exits = (
            Exit.objects.all()
            .filter(
                models.Q(room_1=self.current_location)
                | models.Q(room_2=self.current_location),
            )
            .values_list("room_1__pk", "room_2__pk", "one_to_two", "two_to_one")
        )

        return [
            (
                (one_to_two, room_2_pk)
                if room_1_pk == self.current_location.pk
                else (two_to_one, room_1_pk)
            )
            for room_1_pk, room_2_pk, one_to_two, two_to_one in exits
        ]

    def get_available_exits(self):
        """returns tuple pairs (exit direction label, room.pk)."""
        exits = (
            Exit.objects.filter(
                models.Q(room_1=self.current_location)
                | models.Q(room_2=self.current_location),
            )
            .select_related("room_1", "room_2")
            .prefetch_related("room_1__required_items", "room_2__required_items")
        )

        current_inventory = self.get_inventory()

        available_exit_data = []

        for location_exit in exits:
            moving_to = (
                location_exit.room_2
                if self.current_location == location_exit.room_1
                else location_exit.room_1
            )
            exit_label = (
                location_exit.one_to_two
                if self.current_location == location_exit.room_1
                else location_exit.two_to_one
            )

            if moving_to.required_items.exists() and any(
                not item.in_inventory for item in moving_to.required_items.all()
            ):
                continue

            available_exit_data.append((exit_label, moving_to.pk))

        return available_exit_data
