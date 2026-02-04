from django.db import models

# Create your models here.

class GameManager(models.Manager):

    def playable(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        if "start_room" not in kwargs:
            qs = qs.filter(start_room__isnull=False)

        return qs

class Game(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    start_room = models.OneToOneField("room.Room", related_name="starts_game", null=True, on_delete=models.SET_NULL)

    objects = GameManager()

    def __str__(self):
        return self.name