from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import actions, serializers
from tbac import models


@api_view(["GET"])
def get_game_name(request, game_pk):
    game = models.Game.objects.get(pk=game_pk)
    return Response({"name": game.name})


@api_view(["POST"])
def update_game_name(request, game_pk):
    game = models.Game.objects.get(pk=game_pk)
    serializer = serializers.GameNameSerializer(data=request.data)
    if serializer.is_valid():
        game.name = serializer.validated_data["name"]
        game.save()
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_exit_to_room(request, room_pk):
    room = models.Room.objects.get(pk=room_pk)
    serializer = serializers.AddExitSerializer(data=request.data)
    if serializer.is_valid():
        if models.Exit.objects.filter(
            Q(room_1=room, room_2=serializer.validated_data["room_2"])
            | Q(room_1=serializer.validated_data["room_2"], room_2=room)
        ).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": {"duplicate": ["You already have that connection."]}},
            )

        models.Exit.objects.create(
            room_1=room,
            room_2=serializer.validated_data["room_2"],
            is_locked=serializer.validated_data.get("is_locked", False),
            key_required=serializer.validated_data.get("key_required"),
            leave_room_1=serializer.validated_data["leave_room_1"],
            leave_room_2=serializer.validated_data["leave_room_2"],
        )
        return Response(status=status.HTTP_200_OK)

    return Response(
        status=status.HTTP_400_BAD_REQUEST,
        data={"errors": serializer.errors},
    )


@api_view(["GET"])
def get_exit_data(request, game_pk):
    game = models.Game.objects.get(pk=game_pk)
    return Response(
        {
            "exits": models.Exit.objects.base()
            .filter(room_1__game=game)
            .values("pk", "room_1__name", "room_2__name", "is_locked")
        }
    )


@api_view(["POST"])
def perform_attack_round(request, session_pk):
    session = models.Session.objects.get(pk=session_pk)
    player = session.player
    serializer = serializers.AttackSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": "Unknown attack or enemy reference."},
        )

    enemy = serializer.validated_data["enemy"]
    actions.perform_player_attack(
        session=session,
        enemy=enemy,
        attack_pk=serializer.validated_data["attack_pk"],
    )

    remaining_enemies = session.enemies.filter(
        room=session.current_location, is_dead=False
    )

    actions.perform_enemy_attack(player=player, enemies=remaining_enemies)

    return Response(
        status=status.HTTP_200_OK,
        data={
            "remaining_enemies_count": remaining_enemies.count(),
            "player_is_dead": player.current_health == 0,
        },
    )


@api_view(["GET"])
def get_enemy_table_data(request, session_pk):
    session = models.Session.objects.get(pk=session_pk)
    remaining_enemies = session.enemies.filter(
        room=session.current_location, is_dead=False
    )

    return Response(
        status=status.HTTP_200_OK,
        data={
            "enemies": [
                {
                    "pk": enemy.pk,
                    "name": enemy.name,
                    "health_bar_percentage": enemy.get_health_bar_percentage(),
                    "current_health": enemy.current_health,
                    "max_heath": enemy.health,
                    "description": enemy.description,
                }
                for enemy in remaining_enemies
            ],
        },
    )


@api_view(["GET"])
def get_player_table_data(request, session_pk):
    session = models.Session.objects.select_related("player").get(pk=session_pk)

    return Response(
        status=status.HTTP_200_OK,
        data={
            "player": {
                "health_bar_percentage": session.player.get_health_bar_percentage(),
                "current_health": session.player.current_health,
                "max_heath": session.player.health,
            },
        },
    )


@api_view(["GET"])
def get_network_data(request, game_pk):
    game = models.Game.objects.get(pk=game_pk)

    rooms = game.rooms.base()

    exits = models.Exit.objects.base().filter(room_1__game=game)

    return Response(
        status=status.HTTP_200_OK,
        data={
            "nodes": [{"id": room.pk, "label": room.name} for room in rooms],
            "edges": [
                {
                    "id": exit_.pk,
                    "from": exit_.room_1.pk,
                    "to": exit_.room_2.pk,
                    "dashes": exit_.is_locked,
                }
                for exit_ in exits
            ],
        },
    )


@api_view(["POST"])
def add_new_node(request, game_pk):
    game = models.Game.objects.get(pk=game_pk)

    serializer = serializers.NewNodeSerializer(data=request.data)
    if serializer.is_valid():
        room = models.Room.objects.create(
            game=game,
            name=serializer.validated_data["name"],
        )

        return Response(status=status.HTTP_200_OK, data={"room_id": room.pk})

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_new_edge(request, game_pk):
    game = models.Game.objects.get(pk=game_pk)

    serializer = serializers.NewEdgeSerializer(data=request.data, game_pk=game_pk)

    if serializer.is_valid():
        exit_ = models.Exit.objects.create(
            room_1=serializer.validated_data["from_room"],
            room_2=serializer.validated_data["to_room"],
        )

        return Response(status=status.HTTP_200_OK, data={"exit_id": exit_.pk})

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def delete_node(request, node_pk):
    room = get_object_or_404(models.Room, pk=node_pk)
    room.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def delete_edge(request, edge_pk):
    exit_ = get_object_or_404(models.Exit, pk=edge_pk)
    exit_.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def update_node(request, node_pk):
    room = get_object_or_404(models.Room.objects.select_related("game"), pk=node_pk)

    data = request.data
    data["required_items"] = [int(i) for i in data["required_items"]]

    serializer = serializers.UpdateRoomSerializer(data=data)
    if serializer.is_valid():
        room.name = serializer.validated_data["name"]
        room.accepted_names = serializer.validated_data["accepted_names"]
        room.description = serializer.validated_data["description"]
        room.visited_description = serializer.validated_data["visited_description"]
        room.required_items.set(serializer.validated_data.get("required_items", []))
        room.save()

        return Response(status=status.HTTP_200_OK, data={"room_name": room.name})

    return Response(
        status=status.HTTP_400_BAD_REQUEST, data={"errors": serializer.errors}
    )


@api_view(["GET"])
def get_node_data(request, node_pk):
    room = get_object_or_404(models.Room, pk=node_pk)
    return Response(
        status=status.HTTP_200_OK,
        data={
            "name": room.name,
            "accepted_names": room.accepted_names,
            "description": room.description,
            "visited_description": room.visited_description,
            "required_items": room.required_items.values_list("pk", flat=True),
        },
    )
