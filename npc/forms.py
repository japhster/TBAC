from django import forms

from tbac import models


class GiftedItemForm(forms.Form):
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
        )


class AcceptedItemForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=models.Item.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    hides_dialogue = forms.ModelMultipleChoiceField(
        queryset=models.FriendDialogueOption.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )
    reveals_dialogue = forms.ModelMultipleChoiceField(
        queryset=models.FriendDialogueOption.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )

    def __init__(self, *args, game_pk, friend_pk, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = models.Item.objects.base().filter(
            game_id=game_pk,
        )
        self.fields["hides_dialogue"].queryset = (
            models.FriendDialogueOption.objects.filter(
                friend_id=friend_pk,
            )
        )
        self.fields["reveals_dialogue"].queryset = (
            models.FriendDialogueOption.objects.filter(
                friend_id=friend_pk,
            )
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


class DialogueForm(forms.Form):
    talking_point = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
    can_back_out = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        initial=True,
    )
    is_hidden = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
    )
