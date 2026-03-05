import re

from . import constants


def split_accepted_names(names):
    return [i for i in re.split(", ?", names.lower()) if i]


def get_room_pk(session, args):
    available_rooms = session.get_available_rooms()
    if len(available_rooms) == 1 and not args:
        return available_rooms[0].pk

    for room in available_rooms:
        accepted_names = split_accepted_names(room.accepted_names)
        if args == room.name.lower() or args in accepted_names:
            return room.pk


def get_item_pk(session, args, in_possession=True):
    item_list = session.items.filter(
        **(
            {"room": session.current_location}
            if not in_possession
            else {"in_inventory": True}
        )
    ).values_list("pk", "name", "accepted_names")
    for pk, name, accepted_names in item_list:
        print(pk, name, accepted_names)
        accepted_names = split_accepted_names(accepted_names)
        if args == name.lower() or args in accepted_names:
            return pk


COMMAND_MAP = {
    # Command string: (view name, kwarg name for view, func to retrieve pk)
    constants.MOVE_COMMAND: ("game:move", "room_pk", get_room_pk),
    constants.TAKE_COMMAND: (
        "game:take",
        "item_pk",
        lambda *args, **kwargs: get_item_pk(*args, **kwargs, in_possession=False),
    ),
    constants.DROP_COMMAND: ("game:drop", "item_pk", get_item_pk),
    constants.OPEN_COMMAND: ("game:open", "item_pk", get_item_pk),
    constants.USE_COMMAND: ("game:use", "item_pk", get_item_pk),
}
