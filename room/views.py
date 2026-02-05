from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from . import models, forms
from game.models import Game
from tbac import links, helpers

# Create your views here.


def create_room(request, game_pk):
    game = get_object_or_404(Game, pk=game_pk)
    form = forms.RoomForm(request.POST or None)

    dashboard_link = reverse("game:dashboard", kwargs={"game_pk": game_pk})

    if request.method == "POST" and form.is_valid():
        room = models.Room.objects.create(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            game=game,
        )
        return HttpResponseRedirect(dashboard_link)

    return render(
        request,
        "room/room_form.html",
        context={
            "game": game,
            "form": form,
            "links": [links.game_dashboard(game.pk)],
        },
    )


def edit_room(request, room_pk):
    room = get_object_or_404(models.Room, pk=room_pk)
    form = forms.RoomForm(
        request.POST or None,
        initial={
            "name": room.name,
            "description": room.description,
        },
    )

    dashboard_link = reverse("game:dashboard", kwargs={"game_pk": room.game.pk})

    if request.method == "POST" and form.is_valid():
        room.name = form.cleaned_data["name"]
        room.description = form.cleaned_data["description"]
        room.save()
        return HttpResponseRedirect(dashboard_link)

    return render(
        request,
        "room/room_form.html",
        context={
            "editing": True,
            "form": form,
            "links": [links.game_dashboard(room.game.pk)],
        },
    )


def set_as_starting_room(request, room_pk):
    game = get_object_or_404(Game, rooms__id=room_pk)
    game.start_room_id = room_pk
    game.save()

    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game.pk})


def delete_room(request, room_pk):
    room = get_object_or_404(models.Room.objects.select_related("game"), pk=room_pk)
    game_pk = room.game.pk
    room.delete()

    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})


def create_exit(request, game_pk):
    game = get_object_or_404(Game, pk=game_pk)
    form = forms.ExitForm(request.POST or None, game_pk=game_pk)

    if request.method == "POST" and form.is_valid():
        new_exit = models.Exit.objects.create(
            room_1=form.cleaned_data["room_1"],
            room_2=form.cleaned_data["room_2"],
            one_to_two=form.cleaned_data["one_to_two"],
            two_to_one=form.cleaned_data["two_to_one"],
        )

        return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})

    return render(
        request,
        "room/exit_form.html",
        context={
            "game": game,
            "form": form,
            "links": [links.game_dashboard(game.pk)],
        },
    )


def edit_exit(request, game_pk, exit_pk):
    room_exit = get_object_or_404(models.Exit, pk=exit_pk)
    print(room_exit.room_1, room_exit.room_2)
    form = forms.ExitForm(
        request.POST or None,
        game_pk=game_pk,
        initial={
            "room_1": room_exit.room_1.pk,
            "room_2": room_exit.room_2.pk,
            "one_to_two": room_exit.one_to_two,
            "two_to_one": room_exit.two_to_one,
        },
    )

    if request.method == "POST" and form.is_valid():
        room_exit.room_1 = form.cleaned_data["room_1"]
        room_exit.room_2 = form.cleaned_data["room_2"]
        room_exit.one_to_two = form.cleaned_data["one_to_two"]
        room_exit.two_to_one = form.cleaned_data["two_to_one"]
        room_exit.save()

        return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})

    return render(
        request,
        "room/exit_form.html",
        context={
            "editing": True,
            "form": form,
            "links": [links.game_dashboard(game_pk)],
        },
    )


def delete_exit(request, exit_pk):
    room_exit = get_object_or_404(
        models.Exit.objects.select_related("room_1__game"), pk=exit_pk
    )
    game_pk = room_exit.room_1.game.pk
    room_exit.delete()

    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})
