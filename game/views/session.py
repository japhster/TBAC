from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from .. import constants, forms, interpreter
from item.models import Item
from room.models import Exit, Room
from tbac import helpers, models


def _session_redirect(session_pk):
    return helpers.custom_redirect("game:play", kwargs={"session_pk": session_pk})


def _copy_item(session, item, room_map, item_map):
    old_pk = item.pk
    item.pk = None
    item.session = session
    item.room_id = room_map.get(item.room_id)
    if item.contained_within is not None:
        new_container_pk = item_map.get(item.contained_within_id)
        if new_container_pk is None:
            new_container_pk = _copy_item(
                session, item.contained_within, room_map, item_map
            )
        item.contained_within_id = new_container_pk
    if item.item_type == models.Item.ItemTypeChoices.WEAPON:
        item.damage = models.DamageOutput.objects.create(
            min_damage=item.damage.min_damage,
            max_damage=item.damage.max_damage,
        )
    item.save()

    item_map[old_pk] = item.pk

    return item.pk


def _copy_dialogue_option(session, dialogue_option, friend_map, dialogue_map):
    old_pk = dialogue_option.pk
    dialogue_option.pk = None
    dialogue_option.session = session
    dialogue_option.friend_id = friend_map[dialogue_option.friend_id]
    if dialogue_option.requires_dialogue is not None:
        new_requires_dialogue_pk = dialogue_map.get(
            dialogue_option.requires_dialogue_id
        )
        if new_requires_dialogue_pk is None:
            new_requires_dialogue_pk = _copy_dialogue_option(
                session, dialogue_option.requires_dialogue, friend_map, dialogue_map
            )
        dialogue_option.requires_dialogue_id = new_requires_dialogue_pk
    dialogue_option.save()

    dialogue_map[old_pk] = dialogue_option.pk

    return dialogue_option.pk


@login_required
def start_session(request, game_pk):
    """Attempt to get an existing session of the game passed based on the
    logged in user id.

    Ask the user whether they wish to continue or restart the game and respond in kind.
    """

    game = get_object_or_404(models.Game.objects.all(), pk=game_pk)

    try:
        existing_session = models.Session.objects.get(game=game, user=request.user)
    except models.Session.DoesNotExist:
        return helpers.custom_redirect("game:new_session", kwargs={"game_pk": game_pk})

    form = forms.ContinueGameForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["continue_adventure"]:
            return _session_redirect(existing_session.pk)
        else:
            existing_session.delete()
            return helpers.custom_redirect(
                "game:new_session", kwargs={"game_pk": game_pk}
            )

    return render(request, "game/continue.html", context={"game": game, "form": form})


@login_required
def start_new_session(request, game_pk):
    game = get_object_or_404(
        models.Game.objects.prefetch_related("rooms", "items"), pk=game_pk
    )
    form = forms.NewSessionForm(request.POST or None)
    if request.method != "POST" or not form.is_valid():
        return render(
            request, "game/new_session.html", context={"game": game, "form": form}
        )

    session = models.Session.objects.create(
        game=game,
        user=request.user,
    )

    player = models.Player.objects.create(
        session=session,
        name=form.cleaned_data["name"],
        health=game.starting_health,
        current_health=game.starting_health,
        base_damage=models.DamageOutput.objects.create(
            min_damage=game.base_damage.min_damage,
            max_damage=game.base_damage.max_damage,
        ),
    )

    # a map of the old room pk to the new room pk
    room_map = {}
    room_required_items_map = {}

    for room in game.rooms.base():
        required_items = room.required_items.values_list("pk", flat=True)
        old_pk = room.pk
        room.pk = None
        room.session = session
        room.save()
        room_required_items_map[room.pk] = required_items
        if game.start_room.pk == old_pk:
            session.current_location = room
            session.save()
        room_map[old_pk] = room.pk

    # a map of the old item pk to the new item pk
    item_map = {}

    for item in game.items.base():
        _copy_item(
            session=session,
            item=item,
            room_map=room_map,
            item_map=item_map,
        )

    for room_pk, required_items in room_required_items_map.items():
        session.rooms.get(pk=room_pk).required_items.set(
            Item.objects.session(session.pk).filter(
                pk__in=[item_map[old_pk] for old_pk in required_items]
            )
        )

    for room_exit in Exit.objects.base().filter(
        Q(room_1__game=game) | Q(room_2__game=game)
    ):
        room_exit.pk = None
        room_exit.room_1_id = room_map[room_exit.room_1_id]
        room_exit.room_2_id = room_map[room_exit.room_2_id]
        room_exit.session = session
        if room_exit.is_locked:
            room_exit.key_required_id = item_map[room_exit.key_required_id]
        room_exit.save()

    for end_state in game.end_states.base():
        new_owned_items = [
            item_map[pk]
            for pk in end_state.owned_items.base().values_list("pk", flat=True)
        ]
        end_state.pk = None
        end_state.session = session
        if end_state.location_id is not None:
            end_state.location_id = room_map[end_state.location_id]
        end_state.save()
        end_state.owned_items.set(Item.objects.filter(pk__in=new_owned_items))

    friend_map = {}
    dialogue_map = {}

    for friend in game.friends.base():
        old_pk = friend.pk
        friend.pk = None
        friend.room_id = room_map[friend.room.pk]
        friend.session = session
        friend.save()
        friend_map[old_pk] = friend.pk

    for dialogue_option in models.FriendDialogueOption.objects.filter(
        friend__game=game
    ):
        _copy_dialogue_option(
            session=session,
            dialogue_option=dialogue_option,
            friend_map=friend_map,
            dialogue_map=dialogue_map,
        )

    for accepted_item in models.FriendAcceptsItem.objects.filter(game=game):
        hides_dialogue_old_pks = accepted_item.hides_dialogue.values_list(
            "pk", flat=True
        )
        reveals_dialogue_old_pks = accepted_item.reveals_dialogue.values_list(
            "pk", flat=True
        )
        accepted_item.pk = None
        accepted_item.item_id = item_map[accepted_item.item.pk]
        accepted_item.friend_id = friend_map[accepted_item.friend.pk]
        accepted_item.session = session
        accepted_item.save()
        accepted_item.hides_dialogue.set(
            [dialogue_map[pk] for pk in hides_dialogue_old_pks]
        )
        accepted_item.reveals_dialogue.set(
            [dialogue_map[pk] for pk in reveals_dialogue_old_pks]
        )

    for gift in game.friend_gifts.base():
        gift.pk = None
        gift.friend_id = friend_map[gift.friend.pk]
        gift.dialogue_option_id = dialogue_map[gift.dialogue_option.pk]
        gift.item_id = item_map[gift.item.pk]
        gift.session = session
        gift.save()

    enemy_map = {}

    for enemy in game.enemies.base():
        old_pk = enemy.pk
        enemy.pk = None
        enemy.room_id = room_map[enemy.room.pk]
        enemy.session = session
        enemy.damage = models.DamageOutput.objects.create(
            min_damage=enemy.damage.min_damage,
            max_damage=enemy.damage.max_damage,
        )
        enemy.current_health = enemy.health
        enemy.save()
        enemy_map[old_pk] = enemy.pk

    for drop in game.enemy_drops.base():
        drop.pk = None
        drop.enemy_id = enemy_map[drop.enemy.pk]
        drop.item_id = item_map[drop.item.pk]
        drop.session = session
        drop.save()

    return _session_redirect(session.pk)


@login_required
def play_game(request, session_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    game = session.game

    for end_state in session.end_states.all():
        if end_state.end_state_met():
            return render(
                request,
                "game/end.html",
                context={
                    "session": session,
                    "game": game,
                    "end_state": end_state,
                },
            )

    if session.player.current_health == 0:
        return render(
            request,
            "game/end.html",
            context={
                "session": session,
                "game": session.game,
                "end_state": None,
            },
        )

    location = session.current_location

    if location.visited and location.visited_description:
        location_description = location.visited_description
    else:
        location_description = location.description

    location_description += " " + ". ".join(
        location.items.all().values_list("in_room_description", flat=True)
    )

    return render(
        request,
        "game/session/play.html",
        context={
            "session": session,
            "game": game,
            "location_description": location_description,
            "friend_descriptions": location.friends.values_list(
                "in_room_description", flat=True
            ),
            "enemy_descriptions": location.enemies.exclude(is_dead=True).values_list(
                "in_room_description", flat=True
            ),
            "inventory": session.get_inventory(),
            "form": forms.CommandForm(),
        },
    )


@login_required
def interpret_command(request, session_pk):
    if request.method != "POST":
        return _session_redirect(session_pk)

    form = forms.CommandForm(request.POST or None)
    if not form.is_valid():
        messages.add_message(
            request, messages.INFO, constants.FAILED_TO_INTERPRET_COMMAND_MESSAGE
        )
        return _session_redirect(session_pk)

    session = get_object_or_404(models.Session, pk=session_pk)

    command = form.cleaned_data["command"]
    redirect_view, kwarg_key, interpreter_function = interpreter.COMMAND_MAP.get(
        command, [None, None, None]
    )
    if kwarg_key is None and interpreter_function is None:
        return helpers.custom_redirect(redirect_view, kwargs={"session_pk": session_pk})

    if interpreter_function is None:
        return _session_redirect(session_pk)

    pk = interpreter_function(
        request=request,
        session=session,
        command=command,
        args=form.cleaned_data["args"],
    )
    if pk is None:
        return _session_redirect(session_pk)

    return helpers.custom_redirect(
        redirect_view,
        kwargs={
            "session_pk": session_pk,
            kwarg_key: pk,
        },
    )


@login_required
def move_room(request, session_pk, room_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    room = get_object_or_404(session.rooms.all(), pk=room_pk)

    for item in room.required_items.all():
        if not item.in_inventory:
            return _session_redirect(session_pk)

    current_location = session.current_location
    current_location.visited = True
    current_location.save()

    session.current_location = room
    session.save()
    return _session_redirect(session_pk)


@login_required
def leave_room(request, session_pk):
    session = get_object_or_404(models.Session, pk=session_pk)

    pk = interpreter.get_room_pk(request, session, "GO", args=[])
    if not pk:
        return _session_redirect(session_pk)

    return helpers.custom_redirect(
        "game:move", kwargs={"session_pk": session_pk, "room_pk": pk}
    )


@login_required
def take_item(request, session_pk, item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    item = get_object_or_404(session.items.all(), pk=item_pk)

    if not item.can_be_taken:
        messages.add_message(
            request, messages.INFO, f"The {item.name} cannot be taken."
        )
        return _session_redirect(session_pk)

    item.in_inventory = True
    item.room = None
    item.save()
    return _session_redirect(session_pk)


@login_required
def open_item(request, session_pk, item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    container = get_object_or_404(
        session.items.all(),
        pk=item_pk,
        in_inventory=True,
        item_type=Item.ItemTypeChoices.CONTAINER,
    )

    if (
        container.container_is_locked and container.container_key_required.in_inventory
    ) or not container.container_is_locked:
        container.contents.all().update(in_inventory=True, room=None)
        if container.container_discard_after_open:
            container.in_inventory = False
            container.save()

    return _session_redirect(session_pk)


@login_required
def use_item(request, session_pk, item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    item = get_object_or_404(session.items.all(), pk=item_pk)

    if item.in_inventory and item.item_type == models.Item.ItemTypeChoices.KEY:
        unlocked = session.exits.filter(
            Q(room_1=session.current_location) | Q(room_2=session.current_location),
            key_required=item,
        ).update(is_locked=False)
        if unlocked:
            messages.add_message(
                request, messages.INFO, f"You used the {item.name} to unlock the way."
            )
        else:
            messages.add_message(
                request, messages.INFO, f"That doesn't seem to do unlock anything here."
            )
    else:
        messages.add_message(
            request, messages.INFO, f"You don't know how to use the {item.name}"
        )

    return _session_redirect(session_pk)


@login_required
def inspect_item(request, session_pk, item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    item = get_object_or_404(session.items.all(), pk=item_pk)

    if item.in_inventory or item.room == session.current_location:
        messages.add_message(request, messages.INFO, item.description)

    return _session_redirect(session_pk)


@login_required
def fight_enemy(request, session_pk, enemy_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    enemy = get_object_or_404(session.enemies.all(), pk=enemy_pk)

    if enemy.current_health == 0:
        return helpers.custom_redirect(
            "game:fight_won", kwargs={"session_pk": session_pk, "enemy_pk": enemy_pk}
        )

    player = session.player

    fight_options = [
        {
            "attack_pk": 0,
            "attack_name": "Punch",
            "attack_damage": player.base_damage,
        }
    ] + (
        [
            {
                "attack_pk": weapon.pk,
                "attack_name": weapon.name,
                "attack_damage": weapon.damage,
            }
            for weapon in session.items.filter(
                item_type=models.Item.ItemTypeChoices.WEAPON
            )
        ]
    )

    return render(
        request,
        "game/session/fight.html",
        context={
            "session": session,
            "enemy": enemy,
            "player": player,
            "fight_options": fight_options,
            "enemy_health_bar_width": (enemy.current_health / enemy.health) * 100,
            "player_health_bar_width": (player.current_health / player.health) * 100,
        },
    )


@login_required
def attack_enemy(request, session_pk, enemy_pk, attack_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    enemy = get_object_or_404(session.enemies.all(), pk=enemy_pk)

    if attack_pk == 0:
        attack_damage = session.player.base_damage
    else:
        weapon = session.items.get(pk=attack_pk)
        attack_damage = weapon.damage

    enemy.current_health = max(enemy.current_health - attack_damage.get_damage(), 0)
    enemy.save()

    if enemy.current_health == 0:
        return helpers.custom_redirect(
            "game:fight_won", kwargs={"session_pk": session_pk, "enemy_pk": enemy_pk}
        )

    return helpers.custom_redirect(
        "game:enemy_attack", kwargs={"session_pk": session_pk, "enemy_pk": enemy_pk}
    )


@login_required
def enemy_attack(request, session_pk, enemy_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    enemy = get_object_or_404(session.enemies.all(), pk=enemy_pk)

    player = session.player

    player.current_health = max(player.current_health - enemy.damage.get_damage(), 0)
    player.save()

    if player.current_health == 0:
        return render(
            request,
            "game/end.html",
            context={
                "session": session,
                "game": session.game,
                "end_state": None,
                "killed_by": enemy,
            },
        )

    return helpers.custom_redirect(
        "game:fight", kwargs={"session_pk": session_pk, "enemy_pk": enemy_pk}
    )


@login_required
def fight_won(request, session_pk, enemy_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    enemy = get_object_or_404(session.enemies.filter(current_health=0), pk=enemy_pk)

    if enemy.is_dead:
        messages.add_message(
            request,
            messages.INFO,
            f"You already slew {enemy.name}",
        )

    if enemy.room == session.current_location and not enemy.is_dead:
        enemy.is_dead = True
        enemy.save()
        enemy.get_dropped_items().update(room=session.current_location)
        messages.add_message(request, messages.INFO, f"You slew {enemy.name}!")

    return _session_redirect(session_pk)


@login_required
def talk_to_friend(request, session_pk, friend_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    friend = get_object_or_404(
        session.friends.prefetch_related("dialogue_options", "dialogue_options__gifts"),
        pk=friend_pk,
    )

    if friend.room == session.current_location:
        if friend.dialogue_options.count() == 1:
            dialogue_option = friend.dialogue_options.get()
            dialogue_option.receive_gifts()
            messages.add_message(
                request,
                messages.INFO,
                dialogue_option.text or f"You talked to {friend.name}.",
            )
        else:
            dialogue = get_object_or_404(
                friend.dialogue_options,
                requires_dialogue=None,
                talking_point="",
                is_hidden=False,
            )
            return helpers.custom_redirect(
                "game:discussion",
                kwargs={"session_pk": session_pk, "dialogue_pk": dialogue.pk},
            )

    return _session_redirect(session_pk)


@login_required
def friend_discussion(request, session_pk, dialogue_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    dialogue = get_object_or_404(session.friend_dialogue_options, pk=dialogue_pk)

    dialogue.receive_gifts()

    return render(
        request,
        "game/session/discussion.html",
        context={
            "game": session.game,
            "session": session,
            "dialogue_option": dialogue,
        },
    )


@login_required
def give_item_to_friend(request, session_pk, accepted_item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    accepted_item = get_object_or_404(session.friend_accepts_items, pk=accepted_item_pk)

    item = accepted_item.item
    item.in_inventory = False
    item.save()
    accepted_item.hides_dialogue.update(is_hidden=True)
    accepted_item.reveals_dialogue.update(is_hidden=False)

    messages.add_message(
        request, messages.INFO, f"You gave the {item} to {accepted_item.friend}."
    )

    return _session_redirect(session_pk)
