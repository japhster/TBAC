from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from . import models
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


def start_new_session(request, game_pk):
    game = get_object_or_404(
        models.Game.objects.prefetch_related("rooms", "items"), pk=game_pk
    )
    session = models.Session.objects.create(
        game=game,
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

    return render(
        request,
        "game/play.html",
        context={
            "session": session,
            "game": game,
            "location": session.current_location,
            "exits": session.get_available_exits(),
            "inventory": session.get_inventory(),
            "containers": session.get_openable_containers(),
            "items": session.items.filter(room=session.current_location),
        },
    )


def move_room(request, session_pk, room_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    room = get_object_or_404(session.rooms.all(), pk=room_pk)

    for item in room.required_items.all():
        if not item.in_inventory:
            return _session_redirect(session_pk)

    session.current_location = room
    session.save()
    return _session_redirect(session_pk)


def take_item(request, session_pk, item_pk):
    session = get_object_or_404(models.Session, pk=session_pk)
    item = get_object_or_404(session.items.all(), pk=item_pk)

    item.in_inventory = True
    item.room = None
    item.save()
    return _session_redirect(session_pk)


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
