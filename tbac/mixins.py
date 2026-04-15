import re
from django import forms
from django.db import models

from . import helpers

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
        matching_names = [
            helpers.strip_stop_words(name)
            for name in self.get_accepted_names() + [self.name.lower()]
        ]

        return target_string in matching_names

    class Meta:
        abstract = True


class DamageForm(forms.Form):
    DAMAGE_REQUIRED = True

    min_damage = forms.IntegerField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    max_damage = forms.IntegerField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.DAMAGE_REQUIRED:
            self.fields["min_damage"].required = False
            self.fields["max_damage"].required = False

    def clean(self, *args, **kwargs):
        cd = super().clean(*args, **kwargs)
        if (cd.get("min_damage") or 0) > (cd.get("max_damage") or 0):
            raise forms.ValidationError(
                {
                    "min_damage": "Minimum damage must be less than or equal to the maximum damage."
                }
            )

        return cd
