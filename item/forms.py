from django import forms

from . import models
from room.models import Room
from tbac import mixins


class ItemForm(mixins.DamageForm):
    DAMAGE_REQUIRED = False

    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    accepted_names = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
    in_room_description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
        required=False,
    )
    item_type = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "form-control", "id": "type-filter"}),
        choices=models.Item.ItemTypeChoices.choices,
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    can_be_taken = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        initial=True,
    )

    contained_within = forms.ModelChoiceField(
        queryset=models.Item.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    is_starting_item = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
    )
    healing = forms.IntegerField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
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

        if cd["item_type"] == models.Item.ItemTypeChoices.WEAPON:
            if cd.get("min_damage") is None:
                raise forms.ValidationError(
                    {
                        "min_damage": "Minimum damage is required if item type is 'Weapon'."
                    }
                )
            if cd.get("max_damage") is None:
                raise forms.ValidationError(
                    {
                        "max_damage": "Maximum damage is required if item type is 'Weapon'."
                    }
                )
        if cd["item_type"] == models.Item.ItemTypeChoices.HEALTH:
            if cd.get("healing") is None:
                raise forms.ValidationError(
                    {"healing": "This field is required when creating a health item."}
                )

        return cd
