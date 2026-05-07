from django.db.models import Q

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import serializers
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
            "exits": models.Exit.objects.base().filter(room_1__game=game).values("pk", "room_1__name", "room_2__name", "is_locked")
        }
    )