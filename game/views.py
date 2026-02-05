from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q

from . import forms, models
from room.models import Exit

# Create your views here.


def game_list(request):
    return render(
        request, "game/list.html", context={"games": models.Game.objects.playable()}
    )


def game_detail(request, game_pk, room_pk=None):
    game = get_object_or_404(models.Game, pk=game_pk)

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
        context={"game": game, "room": room, "exits": possible_exits},
    )


def create_game(request):
    form = forms.GameForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        game = models.Game.objects.create(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
        )
        return HttpResponseRedirect(
            reverse("game:dashboard", kwargs={"game_pk": game.pk})
        )

    return render(request, "game/game_form.html", context={"form": form})


def edit_game(request, game_pk):
    game = get_object_or_404(models.Game, pk=game_pk)

    form = forms.GameForm(
        request.POST or None,
        initial={
            "name": game.name,
            "description": game.description,
        },
    )
    if request.method == "POST" and form.is_valid():
        game.name = form.cleaned_data["name"]
        game.description = form.cleaned_data["description"]
        game.save()
        return HttpResponseRedirect(
            reverse("game:dashboard", kwargs={"game_pk": game.pk})
        )

    return render(request, "game/game_form.html", context={"form": form})


def game_dashboard(request, game_pk):
    game = get_object_or_404(
        models.Game.objects.prefetch_related("rooms", "items").select_related(
            "start_room"
        ),
        pk=game_pk,
    )

    all_exits = Exit.objects.filter(
        Q(room_1__game=game) | Q(room_2__game=game)
    ).select_related("room_1", "room_2")

    return render(
        request,
        "game/dashboard.html",
        context={
            "game": game,
            "exits": all_exits,
            "links": [("edit", reverse("game:edit", kwargs={"game_pk": game_pk}))],
        },
    )
