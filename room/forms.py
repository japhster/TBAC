from django import forms

from tbac import models
from item.models import Item


class RoomForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    accepted_names = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )
    visited_description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}), required=False
    )
    required_items = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
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
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    room_2 = forms.ModelChoiceField(
        queryset=models.Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_locked = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
    )
    key_required = forms.ModelChoiceField(
        queryset=models.Item.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room_1"].queryset = models.Room.objects.base().filter(
            game_id=game_pk
        )
        self.fields["room_2"].queryset = models.Room.objects.base().filter(
            game_id=game_pk
        )
        self.fields["key_required"].queryset = models.Item.objects.base().filter(
            game_id=game_pk,
            item_type=models.Item.ItemTypeChoices.KEY,
        )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        if cleaned_data["is_locked"] and cleaned_data["key_required"] is None:
            raise forms.ValidationError({"key_required": "Need to specify which key can open a locked exit."})
