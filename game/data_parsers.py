from django import forms
import json

from tbac import models

EXPECTED_JSON_KEYS = [
    # Keep Alphabetical.
    "end_states",
    "enemies",
    "enemy_drops",
    "exits",
    "friends",
    "friend_accepts_items",
    "friend_dialogue_options",
    "friend_gifts",
    "friend_name_changes",
    "game",
    "items",
    "rooms",
]


def get_export_data(game):
    return {
        "game": {
            "name": game.name,
            "description": game.description,
            "starting_health": game.starting_health,
            "base_damage__min_damage": game.base_damage.min_damage,
            "base_damage__max_damage": game.base_damage.max_damage,
            "start_room": game.start_room.pk,
        },
        "end_states": [
            {
                "is_success": end_state.is_success,
                "name": end_state.name,
                "message": end_state.message,
                "owned_items": list(end_state.owned_items.values_list("pk", flat=True)),
                "location": (
                    end_state.location.pk if end_state.location is not None else None
                ),
            }
            for end_state in game.end_states.base()
        ],
        "rooms": [
            {
                "pk": room.pk,
                "name": room.name,
                "accepted_names": room.accepted_names,
                "description": room.description,
                "visited_description": room.visited_description,
                "required_items": list(
                    room.required_items.values_list("pk", flat=True)
                ),
            }
            for room in game.rooms.base()
        ],
        "exits": list(
            models.Exit.objects.base()
            .filter(room_1__game=game)
            .values(
                "room_1",
                "room_2",
                "is_locked",
                "key_required",
                "leave_room_1",
                "leave_room_2",
            )
        ),
        "items": list(
            game.items.base().values(
                "pk",
                "name",
                "accepted_names",
                "description",
                "in_room_description",
                "item_type",
                "room",
                "can_be_taken",
                "contained_within",
                "is_starting_item",
                "container_is_locked",
                "container_key_required",
                "container_discard_after_open",
                "container_open_name",
                "damage__min_damage",
                "damage__max_damage",
                "healing",
            )
        ),
        "friends": list(
            game.friends.base().values(
                "pk",
                "name",
                "accepted_names",
                "description",
                "in_room_description",
                "room",
            )
        ),
        "enemies": list(
            game.enemies.base().values(
                "pk",
                "name",
                "accepted_names",
                "room",
                "description",
                "in_room_description",
                "health",
                "damage__min_damage",
                "damage__max_damage",
                "auto_fight",
            )
        ),
        "enemy_drops": list(game.enemy_drops.base().values("enemy", "item")),
        "friend_gifts": list(
            game.friend_gifts.base().values("friend", "item", "dialogue_option")
        ),
        "friend_name_changes": list(
            game.friend_name_changes.base().values(
                "friend",
                "dialogue_option",
                "new_name",
                "new_accepted_names",
                "new_description",
                "new_in_room_description",
            )
        ),
        "friend_accepts_items": [
            {
                "friend": item.friend.pk,
                "item": item.item.pk,
                "hides_dialogue": list(
                    item.hides_dialogue.values_list("pk", flat=True)
                ),
                "reveals_dialogue": list(
                    item.reveals_dialogue.values_list("pk", flat=True)
                ),
            }
            for item in game.friend_items_accepted.base()
        ],
        "friend_dialogue_options": list(
            models.FriendDialogueOption.objects.base()
            .filter(friend__game=game)
            .values(
                "pk",
                "friend",
                "requires_dialogue",
                "text",
                "talking_point",
                "can_back_out",
                "is_hidden",
            )
        ),
        "currencies": list(
            models.Currency.objects.filter(game=game).values(
                "pk",
                "name",
                "starting_amount",
            )
        ),
        "shopkeeper_items": list(
            models.ShopkeeperItem.objects.base()
            .filter(game=game)
            .values(
                "shopkeeper",
                "item",
                "price",
                "currency",
            )
        ),
    }


def validate_import_data(data):
    errors = []
    missing_keys = set(EXPECTED_JSON_KEYS).difference(data.keys())
    if missing_keys:
        return [f"Uploaded file is missing keys: {missing_keys}"]

    if models.Game.objects.filter(name=data["game"]["name"]).exists():
        return [f"A game already exists with the name {data['game']['name']}"]

    return []


def import_game(file, imported_by):
    data = json.load(file)
    errors = validate_import_data(data)

    if errors:
        raise forms.ValidationError(errors)

    game = models.Game.objects.create(
        name=data["game"]["name"],
        description=data["game"]["description"],
        starting_health=data["game"]["starting_health"],
        base_damage=models.DamageOutput.objects.create(
            min_damage=data["game"]["base_damage__min_damage"],
            max_damage=data["game"]["base_damage__max_damage"],
        ),
        created_by=imported_by,
    )

    rooms = {}
    for room_row in data["rooms"]:
        rooms[room_row["pk"]] = models.Room.objects.create(
            game=game,
            name=room_row["name"],
            accepted_names=room_row["accepted_names"],
            description=room_row["description"],
            visited_description=room_row["visited_description"],
        )

    items = {}
    for item_row in data["items"]:
        item = models.Item.objects.create(
            game=game,
            room=rooms.get(item_row["room"]),
            name=item_row["name"],
            accepted_names=item_row["accepted_names"],
            description=item_row["description"],
            in_room_description=item_row["in_room_description"],
            item_type=item_row["item_type"],
            can_be_taken=item_row["can_be_taken"],
            is_starting_item=item_row["is_starting_item"],
            container_is_locked=item_row["container_is_locked"],
            container_discard_after_open=item_row["container_discard_after_open"],
            container_open_name=item_row["container_open_name"],
            healing=item_row["healing"],
        )
        if item.item_type == models.Item.ItemTypeChoices.WEAPON:
            item.damage = models.DamageOutput.objects.create(
                min_damage=item_row["damage__min_damage"],
                max_damage=item_row["damage__max_damage"],
            )
            item.save()
        items[item_row["pk"]] = item

    for item_row in data["items"]:
        if item_row["contained_within"] is not None:
            item = items[item_row["pk"]]
            item.contained_within = items[item_row["contained_within"]]
            item.container_key_required = items[item_row["container_key_required"]]
            item.save()

    for room_row in data["rooms"]:
        if room_row["required_items"]:
            room = rooms[room_row["pk"]]
            room.required_items.set(
                [items[old_item_pk] for old_item_pk in room_row["required_items"]]
            )
            room.save()

    game.start_room = rooms[data["game"]["start_room"]]
    game.save()

    for exit_row in data["exits"]:
        models.Exit.objects.create(
            room_1=rooms[exit_row["room_1"]],
            room_2=rooms[exit_row["room_2"]],
            is_locked=exit_row["is_locked"],
            key_required=items.get(exit_row["key_required"]),
            leave_room_1=exit_row["leave_room_1"],
            leave_room_2=exit_row["leave_room_2"],
        )

    for end_state_row in data["end_states"]:
        end_state = models.EndState.objects.create(
            game=game,
            is_success=end_state_row["is_success"],
            name=end_state_row["name"],
            message=end_state_row["message"],
            location=rooms.get(end_state_row["location"]),
        )
        end_state.owned_items.set(
            [items[old_item_pk] for old_item_pk in end_state_row["owned_items"]]
        )
        end_state.save()

    friends = {}
    for friend_row in data["friends"]:
        friends[friend_row["pk"]] = models.Friend.objects.create(
            game=game,
            room=rooms[friend_row["room"]],
            name=friend_row["name"],
            accepted_names=friend_row["accepted_names"],
            description=friend_row["description"],
            in_room_description=friend_row["in_room_description"],
        )

    enemies = {}
    for enemy_row in data["enemies"]:
        enemies[enemy_row["pk"]] = models.Enemy.objects.create(
            game=game,
            room=rooms[enemy_row["room"]],
            name=enemy_row["name"],
            accepted_names=enemy_row["accepted_names"],
            description=enemy_row["description"],
            in_room_description=enemy_row["in_room_description"],
            health=enemy_row["health"],
            damage=models.DamageOutput.objects.create(
                min_damage=enemy_row["damage__min_damage"],
                max_damage=enemy_row["damage__max_damage"],
            ),
            auto_fight=enemy_row["auto_fight"],
        )

    for drop_row in data["enemy_drops"]:
        models.EnemyDrop.objects.create(
            game=game,
            enemy=enemies[drop_row["enemy"]],
            item=items[drop_row["item"]],
        )

    dialogue = {}
    for dialogue_row in data["friend_dialogue_options"]:
        dialogue[dialogue_row["pk"]] = models.FriendDialogueOption.objects.create(
            friend=friends[dialogue_row["friend"]],
            text=dialogue_row["text"],
            talking_point=dialogue_row["talking_point"],
            can_back_out=dialogue_row["can_back_out"],
            is_hidden=dialogue_row["is_hidden"],
        )

    for dialogue_row in data["friend_dialogue_options"]:
        if dialogue_row["requires_dialogue"] is not None:
            dialogue_option = dialogue[dialogue_row["pk"]]
            dialogue_option.requires_dialogue = dialogue[
                dialogue_row["requires_dialogue"]
            ]
            dialogue_option.save()

    for gift_row in data["friend_gifts"]:
        models.FriendGift.objects.create(
            game=game,
            friend=friends[gift_row["friend"]],
            item=items[gift_row["item"]],
            dialogue_option=dialogue[gift_row["dialogue_option"]],
        )

    for name_change_row in data["friend_name_changes"]:
        models.FriendNameChange.objects.create(
            game=game,
            friend=friends[name_change_row["friend"]],
            dialogue_option=dialogue[name_change_row["dialogue_option"]],
            new_name=name_change_row["new_name"],
            new_accepted_names=name_change_row["new_accepted_names"],
            new_description=name_change_row["new_description"],
            new_in_room_description=name_change_row["new_in_room_description"],
        )

    for accepted_row in data["friend_accepts_items"]:
        accepted_item = models.FriendAcceptsItem.objects.create(
            game=game,
            friend=friends[accepted_row["friend"]],
            item=items[accepted_row["item"]],
        )
        accepted_item.hides_dialogue.set(
            [
                dialogue[old_dialogue_pk]
                for old_dialogue_pk in accepted_row["hides_dialogue"]
            ]
        )
        accepted_item.reveals_dialogue.set(
            [
                dialogue[old_dialogue_pk]
                for old_dialogue_pk in accepted_row["reveals_dialogue"]
            ]
        )
        accepted_item.save()

    currencies = {}
    for currency_row in data["currencies"]:
        currencies[currency_row["pk"]] = new_currency = models.Currency.objects.create(
            game=game,
            name=currency_row["name"],
            starting_amount=currency_row["starting_amount"],
        )

    for item_row in data["shopkeeper_items"]:
        models.ShopkeeperItem.objects.create(
            game=game,
            shopkeeper=friends[item_row["shopkeeper"]],
            item=items[item_row["item"]],
            price=item_row["price"],
            currency=currencies[item_row["currency"]],
        )

    return game
