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
        moving_to, direction = exit_.get_exit_room_and_direction(session.current_location)
        if exit_.is_locked:
            locked_rooms.append((moving_to, direction))
            continue
        if moving_to.required_items.exists() and any(
            not item.in_inventory for item in moving_to.required_items.all()
        ):
            blocked_rooms.append((moving_to, direction))
            continue

        available_rooms.append((moving_to, direction))

    if len(available_rooms) == 1 and not args:
        return available_rooms[0][0].pk
    elif len(available_rooms) > 1 and not args:
        messages.add_message(request, messages.INFO, "You're not sure where to go.")
        return

    for room, direction in available_rooms:
        if room.matches(args) or direction.lower() == args.lower():
            return room.pk

    for room in locked_rooms:
        if room.matches(args) or direction.lower() == args.lower():
            messages.add_message(request, messages.INFO, f"That way is locked.")
            return

    for room in blocked_rooms:
        if room.matches(args) or direction.lower() == args.lower():
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


def get_enemy_pk(request, session, command, args, in_room=True):
    enemy_list = session.enemies.all()
    if in_room:
        enemy_list = enemy_list.filter(room=session.current_location)
    for enemy in enemy_list:
        if enemy.matches(args):
            return enemy.pk

    friend_pk = get_friend_pk(
        request, session, command, args, in_room=in_room, silently=True
    )
    if friend_pk:
        messages.add_message(
            request,
            messages.INFO,
            f"{session.friends.get(pk=friend_pk)} is your friend!",
        )
    else:
        messages.add_message(
            request,
            messages.INFO,
            f"You can't figure out how to {command.lower()} {args}",
        )


def get_friend_pk(request, session, command, args, in_room=True, silently=False):
    friend_list = session.friends.all()
    if in_room:
        friend_list = friend_list.filter(room=session.current_location)
    for friend in friend_list:
        if friend.matches(args):
            return friend.pk

    if not silently:
        messages.add_message(
            request,
            messages.INFO,
            f"You can't figure out how to {command.lower()} to {args}",
        )


def get_accepted_item_pk(request, session, command, args):
    for item in session.items.filter(in_inventory=True):
        if item.matches(args):
            accepted_item = session.friend_accepts_items.filter(
                friend__room=session.current_location,
                item=item,
            ).first()
            if accepted_item is not None:
                return accepted_item.pk

    messages.add_message(
        request, messages.INFO, f"You can't give {args} to anyone here."
    )


COMMAND_MAP = {
    # Command string: (view name, kwarg name for view, func to retrieve pk)
    constants.MOVE_COMMAND: ("game:move", "room_pk", get_room_pk),
    constants.LEAVE_COMMAND: ("game:leave", None, None),
    constants.TAKE_COMMAND: (
        "game:take",
        "item_pk",
        lambda *args, **kwargs: get_item_pk(
            *args, **kwargs, in_possession=False, in_room=True
        ),
    ),
    constants.OPEN_COMMAND: ("game:open", "item_pk", get_item_pk),
    constants.USE_COMMAND: ("game:use", "item_pk", get_item_pk),
    constants.INSPECT_COMMAND: (
        "game:inspect",
        "item_pk",
        lambda *args, **kwargs: get_item_pk(*args, **kwargs, in_possession=False),
    ),
    constants.FIGHT_COMMAND: ("game:fight", "enemy_pk", get_enemy_pk),
    constants.TALK_COMMAND: ("game:talk", "friend_pk", get_friend_pk),
    constants.GIVE_COMMAND: ("game:give", "accepted_item_pk", get_accepted_item_pk),
}
