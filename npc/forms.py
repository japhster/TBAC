from django import forms

from tbac import models


class ItemForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=models.Item.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = models.Item.objects.base().filter(
            game_id=game_pk,
            room=None,
            contained_within=None,
            is_starting_item=False,
            enemy_drop=None,
            friend_gift=None,
        )


class FriendForm(forms.Form):
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
    )
    room = forms.ModelChoiceField(
        queryset=models.Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    dialogue = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = models.Room.objects.base().filter(
            game_id=game_pk
        )


class EnemyForm(forms.Form):
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
    )
    room = forms.ModelChoiceField(
        queryset=models.Room.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )

    def __init__(self, *args, game_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = models.Room.objects.base().filter(
            game_id=game_pk
        )
