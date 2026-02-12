from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404

from . import forms, models
from room.models import Exit
from tbac import helpers

# Create your views here.


@login_required
def game_list(request):
    return render(
        request, "game/list.html", context={"games": models.Game.objects.playable(user=request.user)}
    )


def my_games(request):
    return render(
        request,
        "game/my_games.html",
        context={
            "games": models.Game.objects.filter(created_by=request.user),
            "links": [("+ new game", reverse("game:new"))],
        },
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


@login_required
def create_game(request):
    form = forms.GameForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        game = models.Game.objects.create(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            created_by=request.user,
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


@login_required
def game_dashboard(request, game_pk):
    game = get_object_or_404(
        models.Game.objects.filter(created_by=request.user)
        .prefetch_related("rooms", "items")
        .select_related("start_room"),
        pk=game_pk,
    )

    all_exits = (
        Exit.objects.base()
        .filter(Q(room_1__game=game) | Q(room_2__game=game))
        .select_related("room_1", "room_2")
    )

    publish_link = (
        "publish", reverse("game:publish", kwargs={"game_pk": game_pk})
    ) if not game.is_published else (
        "unpublish", reverse("game:unpublish", kwargs={"game_pk": game_pk})
    )

    return render(
        request,
        "game/dashboard.html",
        context={
            "game": game,
            "exits": all_exits,
            "links": [
                ("back", reverse("game:my_games")),
                ("edit", reverse("game:edit", kwargs={"game_pk": game_pk})),
                publish_link,
            ],
        },
    )


@login_required
def publish_game(request, game_pk):
    game = get_object_or_404(models.Game, pk=game_pk, created_by=request.user)

    game.is_published = True
    game.save()
    return helpers.custom_redirect("game:dashboard", {"game_pk": game_pk})


@login_required
def unpublish_game(request, game_pk):
    game = get_object_or_404(models.Game, pk=game_pk, created_by=request.user)

    game.is_published = False
    game.save()
    return helpers.custom_redirect("game:dashboard", {"game_pk": game_pk})

def new_end_state(request, game_pk):
    game = get_object_or_404(models.Game, pk=game_pk)
    form = forms.EndStateForm(
        request.POST or None,
        game_pk=game.pk,
    )

    if request.method == "POST" and form.is_valid():
        end_state = models.EndState.objects.create(
            game=game,
            name=form.cleaned_data["name"],
            message=form.cleaned_data["message"],
            is_success=form.cleaned_data["is_success"],
            location=form.cleaned_data["location"],
        )
        end_state.owned_items.set(form.cleaned_data["owned_items"])

        return HttpResponseRedirect(
            reverse("game:dashboard", kwargs={"game_pk": game.pk})
        )

    return render(
        request,
        "game/end_state_form.html",
        context={
            "game": game,
            "form": form,
            "editing": False,
        },
    )


def edit_end_state(request, end_state_pk):
    end_state = get_object_or_404(
        models.EndState.objects.select_related("game", "location").prefetch_related(
            "owned_items"
        ),
        pk=end_state_pk,
    )
    form = forms.EndStateForm(
        request.POST or None,
        game_pk=end_state.game.pk,
        initial={
            "name": end_state.name,
            "message": end_state.message,
            "is_success": end_state.is_success,
            "location": (
                end_state.location.pk if end_state.location is not None else None
            ),
            "owned_items": end_state.owned_items.values_list("pk", flat=True),
        },
    )

    if request.method == "POST" and form.is_valid():
        end_state.name = form.cleaned_data["name"]
        end_state.message = form.cleaned_data["message"]
        end_state.is_success = form.cleaned_data["is_success"]
        end_state.location = form.cleaned_data["location"]
        end_state.save()
        end_state.owned_items.set(form.cleaned_data["owned_items"])

        return HttpResponseRedirect(
            reverse("game:dashboard", kwargs={"game_pk": end_state.game.pk})
        )

    return render(
        request,
        "game/end_state_form.html",
        context={
            "game": end_state.game,
            "form": form,
            "editing": True,
        },
    )


def delete_end_state(request, end_state_pk):
    end_state = get_object_or_404(
        models.EndState.select_related("game"), pk=end_state_pk
    )
    game_pk = end_state.game.pk
    end_state.delete()

    return HttpResponseRedirect(
        reverse("game:dashboard", kwargs={"game_pk": end_state.game.pk})
    )
