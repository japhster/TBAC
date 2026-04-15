from django import forms

from . import constants
from room.models import Room
from item.models import Item
from tbac import helpers, mixins


class GameForm(mixins.DamageForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )
    starting_health = forms.IntegerField(
        initial=100, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # min_damage = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control"}))
    # max_damage = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control"}))


class NewSessionForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))


class EndStateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))
    location = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    owned_items = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
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


class CommandForm(forms.Form):
    text = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "autofocus": "autofocus"}
        )
    )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        text = cleaned_data["text"].strip().lower()

        command, *args = text.split()

        command = command.upper()

        if command not in constants.ALL_COMMANDS:
            raise forms.ValidationError({"text": "Couldn't figure out the command."})

        for master_command, synonyms in constants.COMMAND_OPTIONS.items():
            if command in synonyms:
                command = master_command
                break

        args = helpers.strip_stop_words(args)

        return {
            "command": command,
            "args": args,
        }
