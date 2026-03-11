from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render, reverse

from . import forms
from tbac import helpers, links, models

# Create your views here.


def _enemy_redirect(enemy_pk):
    return helpers.custom_redirect("npc:enemy", kwargs={"enemy_pk": enemy_pk})


def _friend_redirect(friend_pk):
    return helpers.custom_redirect("npc:friend", kwargs={"friend_pk": friend_pk})


def _dialogue_redirect(dialogue_pk):
    return helpers.custom_redirect("npc:dialogue", kwargs={"dialogue_pk": dialogue_pk})


@login_required
def friend_detail(request, friend_pk):
    friend = get_object_or_404(
        models.Friend.objects.all()
        .select_related("game")
        .prefetch_related("gifts", "gifts__item"),
        pk=friend_pk,
    )
    return render(
        request,
        "npc/friend.html",
        context={
            "friend": friend,
            "links": [
                links.game_dashboard(friend.game.pk),
                ("edit", reverse("npc:edit_friend", kwargs={"friend_pk": friend_pk})),
                (
                    "delete",
                    reverse("npc:delete_friend", kwargs={"friend_pk": friend_pk}),
                ),
            ],
        },
    )


@login_required
def create_friend(request, game_pk):
    game = get_object_or_404(models.Game, pk=game_pk, created_by=request.user)
    form = forms.FriendForm(request.POST or None, game_pk=game_pk)
    if request.method == "POST" and form.is_valid():
        friend = models.Friend.objects.create(
            game=game,
            name=form.cleaned_data["name"],
            accepted_names=form.cleaned_data["accepted_names"],
            description=form.cleaned_data["description"],
            room=form.cleaned_data["room"],
            in_room_description=form.cleaned_data["in_room_description"],
        )
        return _friend_redirect(friend.pk)

    return render(
        request,
        "npc/friend_form.html",
        context={
            "game": game,
            "form": form,
            "links": [links.game_dashboard(game_pk)],
        },
    )


@login_required
def edit_friend(request, friend_pk):
    friend = get_object_or_404(
        models.Friend.objects.select_related("room", "game"),
        pk=friend_pk,
        game__created_by=request.user,
    )
    form = forms.FriendForm(
        request.POST or None,
        game_pk=friend.game.pk,
        initial={
            "name": friend.name,
            "accepted_names": friend.accepted_names,
            "description": friend.description,
            "room": friend.room,
            "in_room_description": friend.in_room_description,
        },
    )
    if request.method == "POST" and form.is_valid():
        friend.name = form.cleaned_data["name"]
        friend.accepted_names = form.cleaned_data["accepted_names"]
        friend.description = form.cleaned_data["description"]
        friend.room = form.cleaned_data["room"]
        friend.in_room_description = form.cleaned_data["in_room_description"]
        friend.save()

        return _friend_redirect(friend.pk)

    return render(
        request,
        "npc/friend_form.html",
        context={
            "game": friend.game,
            "form": form,
            "links": [links.game_dashboard(friend.game.pk)],
            "editing": True,
        },
    )


@login_required
def add_gift_to_dialogue(request, dialogue_pk):
    if request.method != "POST":
        return _dialogue_redirect(dialogue_pk)

    dialogue = get_object_or_404(
        models.FriendDialogueOption.objects.select_related("friend__game"),
        pk=dialogue_pk,
        friend__game__created_by=request.user,
    )
    friend = dialogue.friend
    form = forms.ItemForm(request.POST, game_pk=friend.game.pk)

    if form.is_valid():
        models.FriendGift.objects.create(
            game=friend.game,
            friend=friend,
            item=form.cleaned_data["item"],
            dialogue_option=dialogue,
        )

    return _dialogue_redirect(dialogue_pk)


@login_required
def remove_gift_from_dialogue(request, gift_pk):
    gift = get_object_or_404(models.FriendGift, pk=gift_pk)
    dialogue_pk = gift.dialogue_option.pk
    gift.delete()
    return _dialogue_redirect(dialogue_pk)


@login_required
def delete_friend(request, friend_pk):
    friend = get_object_or_404(
        models.Friend.objects.select_related("game"), pk=friend_pk
    )
    game_pk = friend.game.pk
    friend.delete()

    return helpers.redirect_to_game_dashboard(game_pk)


@login_required
def enemy_detail(request, enemy_pk):
    enemy = get_object_or_404(
        models.Enemy.objects.all()
        .select_related("game")
        .prefetch_related("drops", "drops__item"),
        pk=enemy_pk,
    )
    item_form = forms.ItemForm(game_pk=enemy.game.pk)
    return render(
        request,
        "npc/enemy.html",
        context={
            "enemy": enemy,
            "item_form": item_form,
            "links": [
                links.game_dashboard(enemy.game.pk),
                ("edit", reverse("npc:edit_enemy", kwargs={"enemy_pk": enemy_pk})),
                ("delete", reverse("npc:delete_enemy", kwargs={"enemy_pk": enemy_pk})),
            ],
        },
    )


@login_required
def create_enemy(request, game_pk):
    game = get_object_or_404(models.Game, pk=game_pk, created_by=request.user)
    form = forms.EnemyForm(request.POST or None, game_pk=game_pk)
    if request.method == "POST" and form.is_valid():
        enemy = models.Enemy.objects.create(
            game=game,
            name=form.cleaned_data["name"],
            accepted_names=form.cleaned_data["accepted_names"],
            description=form.cleaned_data["description"],
            room=form.cleaned_data["room"],
            in_room_description=form.cleaned_data["in_room_description"],
        )
        return _enemy_redirect(enemy.pk)

    return render(
        request,
        "npc/enemy_form.html",
        context={
            "game": game,
            "form": form,
            "links": [links.game_dashboard(game_pk)],
        },
    )


@login_required
def edit_enemy(request, enemy_pk):
    enemy = get_object_or_404(
        models.Enemy.objects.select_related("room", "game"),
        pk=enemy_pk,
        game__created_by=request.user,
    )
    form = forms.EnemyForm(
        request.POST or None,
        game_pk=enemy.game.pk,
        initial={
            "name": enemy.name,
            "accepted_names": enemy.accepted_names,
            "description": enemy.description,
            "room": enemy.room.pk,
            "in_room_description": enemy.in_room_description,
        },
    )
    if request.method == "POST" and form.is_valid():
        enemy.name = form.cleaned_data["name"]
        enemy.accepted_names = form.cleaned_data["accepted_names"]
        enemy.description = form.cleaned_data["description"]
        enemy.room = form.cleaned_data["room"]
        enemy.in_room_description = form.cleaned_data["in_room_description"]
        enemy.save()

        return _enemy_redirect(enemy.pk)

    return render(
        request,
        "npc/enemy_form.html",
        context={
            "game": enemy.game,
            "form": form,
            "links": [
                links.game_dashboard(enemy.game.pk),
                (
                    "back to enemy",
                    reverse("npc:enemy", kwargs={"enemy_pk": enemy_pk}),
                ),
            ],
            "editing": True,
        },
    )


@login_required
def add_drop_to_enemy(request, enemy_pk):
    if request.method != "POST":
        return _enemy_redirect(enemy.pk)

    enemy = get_object_or_404(
        models.Enemy.objects.select_related("game"),
        pk=enemy_pk,
        game__created_by=request.user,
    )
    form = forms.ItemForm(request.POST, game_pk=enemy.game.pk)

    if form.is_valid():
        models.EnemyDrop.objects.create(
            game=enemy.game, enemy=enemy, item=form.cleaned_data["item"]
        )

    return _enemy_redirect(enemy.pk)


@login_required
def remove_drop_from_enemy(request, drop_pk):
    drop = get_object_or_404(models.EnemyDrop, pk=drop_pk)
    enemy_pk = drop.enemy.pk
    drop.delete()
    return _enemy_redirect(enemy_pk)


@login_required
def delete_enemy(request, enemy_pk):
    enemy = get_object_or_404(models.Enemy.objects.select_related("game"), pk=enemy_pk)
    game_pk = enemy.game.pk
    enemy.delete()

    return helpers.redirect_to_game_dashboard(game_pk)


@login_required
def dialogue_list(request, friend_pk):
    return render(
        request,
        "npc/dialogue_list.html",
        context={
            "friend": get_object_or_404(
                models.Friend, pk=friend_pk, game__created_by=request.user
            ),
            "dialogue_options": models.FriendDialogueOption.objects.filter(
                friend_id=friend_pk,
                friend__game__created_by=request.user,
            ).values_list("pk", "text"),
            "links": [
                (
                    "back to friend",
                    reverse("npc:friend", kwargs={"friend_pk": friend_pk}),
                ),
            ],
        },
    )


@login_required
def dialogue_detail(request, dialogue_pk):
    dialogue = get_object_or_404(
        models.FriendDialogueOption.objects.select_related("friend").prefetch_related(
            "gifts", "sub_options"
        ),
        pk=dialogue_pk,
        friend__game__created_by=request.user,
    )

    return render(
        request,
        "npc/dialogue.html",
        context={
            "dialogue": dialogue,
            "item_form": forms.ItemForm(game_pk=dialogue.friend.game.pk),
            "links": [
                (
                    "back to dialogue list",
                    reverse(
                        "npc:dialogue_list", kwargs={"friend_pk": dialogue.friend.pk}
                    ),
                ),
                (
                    "edit",
                    reverse("npc:edit_dialogue", kwargs={"dialogue_pk": dialogue_pk}),
                ),
            ],
        },
    )


@login_required
def create_dialogue(request, friend_pk=None, parent_pk=None):
    if friend_pk is None and parent_pk is None:
        raise Http404()

    if friend_pk is not None:
        friend = get_object_or_404(models.Friend, pk=friend_pk)
        parent_option = None
    else:
        parent_option = get_object_or_404(models.FriendDialogueOption, pk=parent_pk)
        friend = parent_option.friend
    form = forms.DialogueForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        dialogue = models.FriendDialogueOption.objects.create(
            friend=friend,
            requires_dialogue=parent_option,
            text=form.cleaned_data["text"],
            talking_point=form.cleaned_data["talking_point"],
        )
        return _dialogue_redirect(dialogue.pk)

    return render(
        request,
        "npc/dialogue_form.html",
        context={
            "form": form,
            "parent_option": parent_option,
            "friend": friend,
            "editing": False,
        },
    )


@login_required
def edit_dialogue(request, dialogue_pk):
    dialogue = get_object_or_404(models.FriendDialogueOption, pk=dialogue_pk)

    form = forms.DialogueForm(
        request.POST or None,
        initial={
            "text": dialogue.text,
            "talking_point": dialogue.talking_point,
        },
    )
    if request.method == "POST" and form.is_valid():
        dialogue.text = form.cleaned_data["text"]
        dialogue.talking_point = form.cleaned_data["talking_point"]
        dialogue.save()

        return _dialogue_redirect(dialogue_pk)

    return render(
        request,
        "npc/dialogue_form.html",
        context={
            "form": form,
            "parent_option": dialogue.requires_dialogue,
            "friend": dialogue.friend,
            "editing": True,
        },
    )
