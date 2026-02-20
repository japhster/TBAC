from django import forms

from . import models
from room.models import Room


class ItemForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
    item_type = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "form-select"}),
        choices=models.Item.ItemTypeChoices.choices,
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )
    contained_within = forms.ModelChoiceField(
        queryset=models.Item.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )
    is_starting_item = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = Room.objects.base().filter(game_id=game_pk)
        self.fields["contained_within"].queryset = models.Item.objects.base().filter(
            game_id=game_pk, item_type=models.Item.ItemTypeChoices.CONTAINER
        )

    def clean(self, *args, **kwargs):
        cd = super().clean(*args, **kwargs)

        room = cd.get("room")
        contained_within = cd.get("contained_within")
        is_starting_item = cd.get("is_starting_item", False)

        if room is None and contained_within is None and not is_starting_item:
            raise forms.ValidationError(
                "The item must either be in a room or container or be a starting item."
            )

        if room is not None and contained_within is not None:
            raise forms.ValidationError(
                "The item does not need a room if it is in a container."
            )

        if room is not None and is_starting_item:
            raise forms.ValidationError(
                "The item does not need a room if it is a starting item."
            )

        if contained_within is not None and is_starting_item:
            raise forms.ValidationError(
                "The item should not be a starting item if it is in a container"
                " (The container should be considered a starting item)."
            )
