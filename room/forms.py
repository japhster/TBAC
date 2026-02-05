from django import forms

from . import models


class RoomForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )


class ExitForm(forms.Form):
    room_1 = forms.ModelChoiceField(
        queryset=models.Room.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    room_2 = forms.ModelChoiceField(
        queryset=models.Room.objects.all(),
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
        self.fields["room_1"].queryset = models.Room.objects.filter(game_id=game_pk)
        self.fields["room_2"].queryset = models.Room.objects.filter(game_id=game_pk)
