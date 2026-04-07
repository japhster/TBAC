from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from . import models, forms
from game.models import Game
from tbac import links, helpers

# Create your views here.


@login_required
def create_room(request, game_pk):
    game = get_object_or_404(Game, pk=game_pk, created_by=request.user)
    form = forms.RoomForm(request.POST or None, game_pk=game_pk)

    dashboard_link = reverse("game:dashboard", kwargs={"game_pk": game_pk})

    if request.method == "POST" and form.is_valid():
        room = models.Room.objects.create(
            name=form.cleaned_data["name"],
            accepted_names=form.cleaned_data["accepted_names"],
            description=form.cleaned_data["description"],
            visited_description=form.cleaned_data["visited_description"],
            game=game,
        )
        room.required_items.set(form.cleaned_data["required_items"])
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


@login_required
def edit_room(request, room_pk):
    room = get_object_or_404(models.Room, pk=room_pk, game__created_by=request.user)
    form = forms.RoomForm(
        request.POST or None,
        initial={
            "name": room.name,
            "accepted_names": room.accepted_names,
            "description": room.description,
            "visited_description": room.visited_description,
            "required_items": room.required_items.values_list("pk", flat=True),
        },
        game_pk=room.game_id,
    )

    dashboard_link = reverse("game:dashboard", kwargs={"game_pk": room.game.pk})

    if request.method == "POST" and form.is_valid():
        room.name = form.cleaned_data["name"]
        room.accepted_names = form.cleaned_data["accepted_names"]
        room.description = form.cleaned_data["description"]
        room.save()
        room.required_items.set(form.cleaned_data["required_items"])

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


@login_required
def set_as_starting_room(request, room_pk):
    game = get_object_or_404(Game, rooms__id=room_pk, created_by=request.user)
    game.start_room_id = room_pk
    game.save()

    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game.pk})


@login_required
def delete_room(request, room_pk):
    room = get_object_or_404(models.Room.objects.select_related("game"), pk=room_pk)
    game_pk = room.game.pk
    room.delete()

    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})


@login_required
def create_exit(request, game_pk):
    game = get_object_or_404(Game, pk=game_pk, created_by=request.user)
    form = forms.ExitForm(request.POST or None, game_pk=game_pk)

    if request.method == "POST" and form.is_valid():
        new_exit = models.Exit.objects.create(
            room_1=form.cleaned_data["room_1"],
            room_2=form.cleaned_data["room_2"],
            is_locked=form.cleaned_data["is_locked"],
            key_required=form.cleaned_data["key_required"],
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


@login_required
def edit_exit(request, game_pk, exit_pk):
    room_exit = get_object_or_404(
        models.Exit, pk=exit_pk, room_1__game__created_by=request.user
    )
    form = forms.ExitForm(
        request.POST or None,
        game_pk=game_pk,
        initial={
            "room_1": room_exit.room_1.pk,
            "room_2": room_exit.room_2.pk,
            "is_locked": room_exit.is_locked,
            "key_required": room_exit.key_required,
        },
    )

    if request.method == "POST" and form.is_valid():
        room_exit.room_1 = form.cleaned_data["room_1"]
        room_exit.room_2 = form.cleaned_data["room_2"]
        room_exit.is_locked = form.cleaned_data["is_locked"]
        room_exit.key_required = form.cleaned_data["key_required"]
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


@login_required
def delete_exit(request, exit_pk):
    room_exit = get_object_or_404(
        models.Exit.objects.select_related("room_1__game"),
        pk=exit_pk,
        game__created_by=request.user,
    )
    game_pk = room_exit.room_1.game.pk
    room_exit.delete()

    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})
