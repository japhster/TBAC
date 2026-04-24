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
        .prefetch_related("gifts", "gifts__item", "store_inventory"),
        pk=friend_pk,
    )
    return render(
        request,
        "npc/friend.html",
        context={
            "friend": friend,
            "links": [
                links.game_dashboard(friend.game.pk, hashtag="friend"),
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
    form = forms.GiftedItemForm(request.POST, game_pk=friend.game.pk)

    if form.is_valid():
        models.FriendGift.objects.create(
            game=friend.game,
            friend=friend,
            item=form.cleaned_data["item"],
            dialogue_option=dialogue,
        )

    return _dialogue_redirect(dialogue_pk)


@login_required
def add_name_change_to_friend(request, friend_pk):
    friend = get_object_or_404(
        models.Friend.objects.all(), pk=friend_pk, game__created_by=request.user
    )

    form = forms.FriendNameChangeForm(request.POST or None, friend_pk=friend.pk)

    if request.method == "POST" and form.is_valid():
        models.FriendNameChange.objects.create(
            game=friend.game,
            friend=friend,
            dialogue_option=form.cleaned_data["dialogue_option"],
            new_name=form.cleaned_data["new_name"],
            new_accepted_names=form.cleaned_data["new_accepted_names"],
            new_description=form.cleaned_data["new_description"],
            new_in_room_description=form.cleaned_data["new_in_room_description"],
        )
        return _friend_redirect(friend_pk)

    return render(
        request,
        "npc/friend_name_change_form.html",
        context={"friend": friend, "form": form},
    )


@login_required
def edit_name_change_for_friend(request, name_change_pk):
    name_change = get_object_or_404(
        models.FriendNameChange.objects.all(),
        pk=name_change_pk,
        game__created_by=request.user,
    )

    form = forms.FriendNameChangeForm(
        request.POST or None,
        friend_pk=name_change.friend.pk,
        initial={
            "dialogue_option": name_change.dialogue_option.pk,
            "new_name": name_change.new_name,
            "new_accepted_names": name_change.new_accepted_names,
            "new_description": name_change.new_description,
            "new_in_room_description": name_change.new_in_room_description,
        },
    )

    if request.method == "POST" and form.is_valid():
        name_change.dialogue_option = form.cleaned_data["dialogue_option"]
        name_change.new_name = form.cleaned_data["new_name"]
        name_change.new_accepted_names = form.cleaned_data["new_accepted_names"]
        name_change.new_description = form.cleaned_data["new_description"]
        name_change.new_in_room_description = form.cleaned_data[
            "new_in_room_description"
        ]
        name_change.save()

        return _friend_redirect(name_change.friend_id)

    return render(
        request,
        "npc/friend_name_change_form.html",
        context={"friend": name_change.friend, "form": form},
    )


@login_required
def add_accepted_item_to_friend(request, friend_pk):
    friend = get_object_or_404(
        models.Friend.objects.all(), pk=friend_pk, game__created_by=request.user
    )

    form = forms.AcceptedItemForm(
        request.POST or None, game_pk=friend.game.pk, friend_pk=friend.pk
    )

    if request.method == "POST" and form.is_valid():
        accepted_item = models.FriendAcceptsItem.objects.create(
            game=friend.game,
            friend=friend,
            item=form.cleaned_data["item"],
        )
        accepted_item.reveals_dialogue.set(form.cleaned_data["reveals_dialogue"])
        accepted_item.hides_dialogue.set(form.cleaned_data["hides_dialogue"])

        return _friend_redirect(friend_pk)

    return render(
        request,
        "npc/accepted_item_form.html",
        context={
            "friend": friend,
            "form": form,
            "links": [
                (
                    "back to friend",
                    reverse("npc:friend", kwargs={"friend_pk": friend_pk}),
                )
            ],
        },
    )


@login_required
def edit_accepted_item(request, accepted_item_pk):
    accepted_item = get_object_or_404(
        models.FriendAcceptsItem.objects.all(),
        pk=accepted_item_pk,
        game__created_by=request.user,
    )

    friend = accepted_item.friend

    form = forms.AcceptedItemForm(
        request.POST or None,
        game_pk=friend.game.pk,
        friend_pk=friend.pk,
        initial={
            "item": accepted_item.item.pk,
            "hides_dialogue": accepted_item.hides_dialogue.values_list("pk", flat=True),
            "reveals_dialogue": accepted_item.reveals_dialogue.values_list(
                "pk", flat=True
            ),
        },
    )

    if request.method == "POST" and form.is_valid():
        accepted_item.item = form.cleaned_data["item"]
        accepted_item.save()

        accepted_item.hides_dialogue.set(form.cleaned_data["hides_dialogue"])
        accepted_item.reveals_dialogue.set(form.cleaned_data["reveals_dialogue"])

        return _friend_redirect(friend.pk)

    return render(
        request,
        "npc/accepted_item_form.html",
        context={
            "friend": friend,
            "form": form,
            "links": [
                (
                    "back to friend",
                    reverse("npc:friend", kwargs={"friend_pk": friend.pk}),
                )
            ],
            "editing": True,
        },
    )


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
    item_form = forms.GiftedItemForm(game_pk=enemy.game.pk)
    return render(
        request,
        "npc/enemy.html",
        context={
            "enemy": enemy,
            "item_form": item_form,
            "links": [
                links.game_dashboard(enemy.game.pk, hashtag="enemy"),
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
            damage=models.DamageOutput.objects.create(
                min_damage=form.cleaned_data["min_damage"],
                max_damage=form.cleaned_data["max_damage"],
            ),
            auto_fight=form.cleaned_data["auto_fight"],
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
            "min_damage": enemy.damage.min_damage,
            "max_damage": enemy.damage.max_damage,
            "auto_fight": enemy.auto_fight,
        },
    )
    if request.method == "POST" and form.is_valid():
        enemy.name = form.cleaned_data["name"]
        enemy.accepted_names = form.cleaned_data["accepted_names"]
        enemy.description = form.cleaned_data["description"]
        enemy.room = form.cleaned_data["room"]
        enemy.in_room_description = form.cleaned_data["in_room_description"]
        enemy.auto_fight = form.cleaned_data["auto_fight"]
        enemy.save()

        damage = enemy.damage
        damage.min_damage = form.cleaned_data["min_damage"]
        damage.max_damage = form.cleaned_data["max_damage"]
        damage.save()

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
    form = forms.GiftedItemForm(request.POST, game_pk=enemy.game.pk)

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

    dialogue_options = models.FriendDialogueOption.objects.filter(
        friend_id=friend_pk,
        friend__game__created_by=request.user,
    ).select_related("requires_dialogue")

    has_active_start_point = dialogue_options.filter(
        requires_dialogue=None, is_hidden=False
    ).exists()

    return render(
        request,
        "npc/dialogue_list.html",
        context={
            "friend": get_object_or_404(
                models.Friend, pk=friend_pk, game__created_by=request.user
            ),
            "dialogue_options": dialogue_options,
            "has_active_start_point": has_active_start_point,
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
            "item_form": forms.GiftedItemForm(game_pk=dialogue.friend.game.pk),
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

    is_new_starting_point = parent_option is None and friend.dialogue_options.exists()

    if request.method == "POST" and form.is_valid():
        dialogue = models.FriendDialogueOption.objects.create(
            friend=friend,
            requires_dialogue=parent_option,
            text=form.cleaned_data["text"],
            talking_point=form.cleaned_data["talking_point"],
            can_back_out=form.cleaned_data["can_back_out"],
            is_hidden=form.cleaned_data["is_hidden"],
        )
        if is_new_starting_point and not form.cleaned_data["is_hidden"]:
            friend.dialogue_options.filter(requires_dialogue=None).exclude(
                pk=dialogue.pk
            ).update(is_hidden=True)

        return _dialogue_redirect(dialogue.pk)

    return render(
        request,
        "npc/dialogue_form.html",
        context={
            "form": form,
            "parent_option": parent_option,
            "friend": friend,
            "editing": False,
            "is_new_starting_point": is_new_starting_point,
            "links": [
                (
                    "back to dialogue tree",
                    reverse("npc:dialogue_list", kwargs={"friend_pk": friend.pk}),
                ),
            ],
        },
    )


@login_required
def edit_dialogue(request, dialogue_pk):
    dialogue = get_object_or_404(models.FriendDialogueOption, pk=dialogue_pk)
    friend = dialogue.friend

    other_start_points = friend.dialogue_options.filter(requires_dialogue=None).exclude(
        pk=dialogue_pk
    )

    is_alternative_starting_point = (
        dialogue.requires_dialogue is None and other_start_points.exists()
    )

    form = forms.DialogueForm(
        request.POST or None,
        initial={
            "text": dialogue.text,
            "talking_point": dialogue.talking_point,
            "can_back_out": dialogue.can_back_out,
            "is_hidden": dialogue.is_hidden,
        },
    )
    if request.method == "POST" and form.is_valid():
        dialogue.text = form.cleaned_data["text"]
        dialogue.talking_point = form.cleaned_data["talking_point"]
        dialogue.can_back_out = form.cleaned_data["can_back_out"]
        dialogue.is_hidden = form.cleaned_data["is_hidden"]
        dialogue.save()

        if is_alternative_starting_point and not form.cleaned_data["is_hidden"]:
            other_start_points.update(is_hidden=True)

        return _dialogue_redirect(dialogue_pk)

    return render(
        request,
        "npc/dialogue_form.html",
        context={
            "form": form,
            "parent_option": dialogue.requires_dialogue,
            "friend": friend,
            "editing": True,
            "is_alternative_starting_point": is_alternative_starting_point,
            "links": [
                (
                    "back to dialogue tree",
                    reverse("npc:dialogue_list", kwargs={"friend_pk": friend.pk}),
                ),
            ],
        },
    )


@login_required
def hide_dialogue(request, dialogue_pk):
    dialogue = get_object_or_404(models.FriendDialogueOption, pk=dialogue_pk)
    dialogue.is_hidden = True
    dialogue.save()

    return helpers.custom_redirect(
        "npc:dialogue_list", kwargs={"friend_pk": dialogue.friend_id}
    )


@login_required
def show_dialogue(request, dialogue_pk):
    dialogue = get_object_or_404(models.FriendDialogueOption, pk=dialogue_pk)
    dialogue.is_hidden = False

    if dialogue.requires_dialogue is None:
        dialogue.friend.dialogue_options.filter(requires_dialogue=None).exclude(
            pk=dialogue_pk
        ).update(is_hidden=True)

    dialogue.save()

    return helpers.custom_redirect(
        "npc:dialogue_list", kwargs={"friend_pk": dialogue.friend_id}
    )


@login_required
def add_store_item_to_shopkeeper(request, shopkeeper_pk):
    shopkeeper = get_object_or_404(
        models.Friend.objects.all(), pk=shopkeeper_pk, game__created_by=request.user
    )

    form = forms.ShopkeeperItemForm(
        request.POST or None,
        game_pk=shopkeeper.game.pk,
    )

    if request.method == "POST" and form.is_valid():
        store_item = models.ShopkeeperItem.objects.create(
            game=shopkeeper.game,
            shopkeeper=shopkeeper,
            item=form.cleaned_data["item"],
            price=form.cleaned_data["price"],
            currency=form.cleaned_data["currency"],
        )

        return _friend_redirect(shopkeeper_pk)

    return render(
        request,
        "npc/store_item_form.html",
        context={
            "shopkeeper": shopkeeper,
            "form": form,
            "links": [
                (
                    "back to friend",
                    reverse("npc:friend", kwargs={"friend_pk": shopkeeper_pk}),
                )
            ],
        },
    )


@login_required
def edit_store_item(request, store_item_pk):
    store_item = get_object_or_404(
        models.ShopkeeperItem.objects.all(),
        pk=store_item_pk,
        game__created_by=request.user,
    )

    shopkeeper = store_item.shopkeeper

    form = forms.ShopkeeperItemForm(
        request.POST or None,
        game_pk=shopkeeper.game.pk,
        initial={
            "item": store_item.item.pk,
            "price": store_item.price,
            "currency": store_item.currency.pk,
        },
    )

    if request.method == "POST" and form.is_valid():
        store_item.item = form.cleaned_data["item"]
        store_item.price = form.cleaned_data["price"]
        store_item.currency = form.cleaned_data["currency"]
        store_item.save()

        return _friend_redirect(shopkeeper.pk)

    return render(
        request,
        "npc/store_item_form.html",
        context={
            "shopkeeper": shopkeeper,
            "form": form,
            "links": [
                (
                    "back to friend",
                    reverse("npc:friend", kwargs={"friend_pk": shopkeeper.pk}),
                )
            ],
            "editing": True,
        },
    )
