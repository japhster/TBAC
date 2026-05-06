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

    return Response
