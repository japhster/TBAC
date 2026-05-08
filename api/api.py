from django.db.models import Q

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
