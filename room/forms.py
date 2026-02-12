from django import forms

from . import models
from item.models import Item


class RoomForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )
    visited_description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}), required=False
    )
    required_items = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
        queryset=Item.objects.none(),
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["required_items"].queryset = Item.objects.base().filter(
            game_id=game_pk
        )


class ExitForm(forms.Form):
    room_1 = forms.ModelChoiceField(
        queryset=models.Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    room_2 = forms.ModelChoiceField(
        queryset=models.Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    one_to_two = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    two_to_one = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room_1"].queryset = models.Room.objects.base().filter(
            game_id=game_pk
        )
        self.fields["room_2"].queryset = models.Room.objects.base().filter(
            game_id=game_pk
        )
