from django.contrib import messages
import re

from . import constants


def split_accepted_names(names):
    return [i for i in re.split(", ?", names.lower()) if i]


def get_room_pk(request, session, command, args):
    exits = session.get_exits()

    available_rooms = []
    locked_rooms = []
    blocked_rooms = []

    for exit_ in exits:
        moving_to = exit_.get_exit_room(session.current_location)
        if exit_.is_locked:
            locked_rooms.append(moving_to)
            continue
        if moving_to.required_items.exists() and any(
            not item.in_inventory for item in moving_to.required_items.all()
        ):
            blocked_rooms.append(moving_to)
            continue

        available_rooms.append(moving_to)

    if len(available_rooms) == 1 and not args:
        return available_rooms[0].pk
    elif len(available_rooms) > 1 and not args:
        messages.add_message(request, messages.INFO, "You're not sure where to go.")
        return

    for room in available_rooms:
        if room.matches(args):
            return room.pk

    for room in locked_rooms:
        if room.matches(args):
            messages.add_message(request, messages.INFO, f"That way is locked.")
            return

    for room in blocked_rooms:
        if room.matches(args):
            messages.add_message(
                request, messages.INFO, f"That way requires something to access."
            )
            return

    messages.add_message(
        request, messages.INFO, f"You're not sure how to get to '{args}' from here"
    )


def get_item_pk(request, session, command, args, in_possession=True, in_room=False):
    item_list = session.items.all()
    if in_possession:
        item_list = item_list.filter(in_inventory=True)
    elif in_room:
        item_list = item_list.filter(room=session.current_location)

    for item in item_list:
        if item.matches(args):
            return item.pk

    messages.add_message(
        request, messages.INFO, f"You don't know how to {command.lower()} the {args}"
    )


COMMAND_MAP = {
    # Command string: (view name, kwarg name for view, func to retrieve pk)
    constants.MOVE_COMMAND: ("game:move", "room_pk", get_room_pk),
    constants.TAKE_COMMAND: (
        "game:take",
        "item_pk",
        lambda *args, **kwargs: get_item_pk(
            *args, **kwargs, in_possession=False, in_room=True
        ),
    ),
    constants.OPEN_COMMAND: ("game:open", "item_pk", get_item_pk),
    constants.USE_COMMAND: ("game:use", "item_pk", get_item_pk),
}
