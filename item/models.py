from django.db import models

# Create your models here.


class Item(models.Model):
    class ItemTypeChoices(models.TextChoices):
        GENERIC = ("GENERIC", "Generic Item")
        KEY = ("KEY", "Key")
        CONTAINER = ("CONTAINER", "Container")
        LIGHT = ("LIGHT", "Light Source")

    name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    item_type = models.CharField(max_length=20, choices=ItemTypeChoices.choices)
    game = models.ForeignKey(
        "game.Game", related_name="items", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "room.Room", related_name="items", on_delete=models.SET_NULL, null=True
    )
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
        "self", related_name="unlocks_containers", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(
                        room__isnull=False,
                        is_starting_item=False,
                        contained_within__isnull=True,
                    )
                    | models.Q(
                        contained_within__isnull=False,
                        is_starting_item=False,
                        room__isnull=True,
                    )
                    | models.Q(
                        is_starting_item=True,
                        room__isnull=True,
                        contained_within__isnull=True,
                    )
                ),
                name="must_have_one_location",
            ),
        ]

    def __str__(self):
        return self.name
