from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect

from . import models
from room.models import Exit

# Create your views here.



def game_list(request):
    return render(
        request,
        "game/list.html",
        context={"games": models.Game.objects.playable()})


def game_detail(request, game_pk, room_pk=None):
    try:
        game = models.Game.objects.get(pk=game_pk)
    except models.Game.DoesNotExist:
        return HttpResponseRedirect(reverse("game:list"))

    if room_pk is not None:
        room = game.rooms.get(pk=room_pk)
    else:
        room = game.start_room

    possible_exits = dict(
        exit_.get_exit_name_and_room_pk(room)
        for exit_ in Exit.objects.from_room(room=room)
    )
    

    return render(
        request,
        "game/detail.html",
        context={
            "game": game,
            "room": room,
            "exits": possible_exits
        }
    )