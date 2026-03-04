import re

from . import constants


def get_room_pk(session, args):
    available_rooms = session.get_available_rooms()
    if len(available_rooms) == 1 and not args:
        return available_rooms[0].pk

    for room in available_rooms:
        accepted_names = [i for i in re.split(", ?", room.accepted_names.lower()) if i]
        print(args, room.name.lower(), accepted_names)
        if args == room.name.lower() or args in accepted_names:
            return room.pk


def get_item_pk(session, args, in_possession=False):
    item_list = session.items.filter(
        **(
            {"room": session.current_location}
            if not in_possession
            else {"in_inventory": True}
        )
    ).values_list("pk", "name")
    for pk, name in item_list:
        if args == name.lower():
            return pk


COMMAND_MAP = {
    # Command string: (view name, kwarg name for view, func to retrieve pk)
    constants.MOVE_COMMAND: ("game:move", "room_pk", get_room_pk),
    constants.TAKE_COMMAND: ("game:take", "item_pk", get_item_pk),
    constants.DROP_COMMAND: (
        "game:drop",
        "item_pk",
        lambda *args, **kwargs: get_item_pk(*args, **kwargs, in_possession=True),
    ),
    constants.OPEN_COMMAND: (
        "game:open",
        "item_pk",
        lambda *args, **kwargs: get_item_pk(*args, **kwargs, in_possession=True),
    ),
}
