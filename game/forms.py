from django import forms

from . import constants
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
    STOP_WORDS = ["to", "the"]
    text = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "autofocus": "autofocus"}
        )
    )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        text = cleaned_data["text"].strip().lower()
        text_list = text.split()
        while True:
            if len(text_list) > 1 and text_list[1] in self.STOP_WORDS:
                text_list = [text_list[0]] + text_list[2:]
            else:
                break

        if text_list[0].upper() not in constants.ALL_COMMANDS:
            raise forms.ValidationError({"text": "Couldn't figure out the command."})

        command = text_list[0].upper()
        for master_command, synonyms in constants.COMMAND_OPTIONS.items():
            if command in synonyms:
                command = master_command
                break
        args = " ".join(text_list[1:])

        return {
            "command": command,
            "args": args,
        }
