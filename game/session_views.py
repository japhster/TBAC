from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from . import constants, forms, interpreter, models
from item.models import Item
from room.models import Exit, Room
from tbac import helpers


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
    item.save()

    item_map[old_pk] = item.pk

    return item.pk


@login_required
def start_session(request, game_pk):
    """Attempt to get an existing session of the game passed based on the
    logged in user id.

    Ask the user whether they wish to continue or restart the game and respond in kind.
    """

    game = get_object_or_404(models.Game.objects.all(), pk=game_pk)

    try:
        existing_session = models.Session.objects.get(game=game, player=request.user)
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
    session = models.Session.objects.create(
        game=game,
        player=request.user,
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
        "game/play.html",
        context={
            "session": session,
            "game": game,
            "location_description": location_description,
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
        return _session_redirect(session_pk)

    session = get_object_or_404(models.Session, pk=session_pk)

    command = form.cleaned_data["command"]
    redirect_view, kwarg_key, interpreter_function = interpreter.COMMAND_MAP.get(
        command, [None, None, None]
    )
    if interpreter_function is None:
        return _session_redirect(session_pk)

    pk = interpreter_function(session, form.cleaned_data["args"])
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
def take_item(request, session_pk, item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    item = get_object_or_404(session.items.all(), pk=item_pk)

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
        exit_to_unlock = session.exits.filter(
            Q(room_1=session.current_location) | Q(room_2=session.current_location),
            key_required=item,
        ).update(is_locked=False)


    return _session_redirect(session_pk)
