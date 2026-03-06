import re

from django.db import models


class SessionManager(models.Manager):
    def base(self):
        return self.get_queryset().filter(session__isnull=True)

    def session(self, session_pk):
        return self.get_queryset().filter(session_id=session_pk)


class SearchableMixin(models.Model):
    name = models.CharField(max_length=250)
    accepted_names = models.CharField(max_length=1000)

    def get_accepted_names(self):
        return [i for i in re.split(", ?", self.accepted_names.lower()) if i]

    def matches(self, target_string):
        target_string = target_string.lower()
        return (
            target_string == self.name.lower()
            or target_string in self.get_accepted_names()
        )

    class Meta:
        abstract = True
