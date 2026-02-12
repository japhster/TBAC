from django import forms

from room.models import Room
from item.models import Item


class GameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )


class EndStateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))
    location = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )
    owned_items = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
        queryset=Item.objects.none(),
    )
    is_success = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        initial=True,
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Room.objects.base().filter(game_id=game_pk)
        self.fields["owned_items"].queryset = Item.objects.base().filter(
            game_id=game_pk
        )


class ContinueGameForm(forms.Form):
    continue_adventure = forms.BooleanField(required=False)
