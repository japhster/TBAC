from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from tbac import helpers, links, models

from . import forms
from game.models import Game

# Create your views here.


@login_required
def create_item(request, game_pk):
    game = get_object_or_404(Game, pk=game_pk, created_by=request.user)
    form = forms.ItemForm(request.POST or None, game_pk=game_pk)

    if request.method == "POST" and form.is_valid():
        new_item = models.Item.objects.create(
            name=form.cleaned_data["name"],
            accepted_names=form.cleaned_data["accepted_names"],
            description=form.cleaned_data["description"],
            in_room_description=form.cleaned_data["in_room_description"],
            item_type=form.cleaned_data["item_type"],
            game=game,
            room=form.cleaned_data["room"],
            can_be_taken=form.cleaned_data["can_be_taken"],
            contained_within=form.cleaned_data["contained_within"],
            is_starting_item=form.cleaned_data["is_starting_item"],
        )
        if new_item.item_type == models.Item.ItemTypeChoices.WEAPON:
            new_item.damage = models.DamageOutput.objects.create(
                min_damage=form.cleaned_data["min_damage"],
                max_damage=form.cleaned_data["max_damage"],
            )
            new_item.save()

        return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})

    return render(
        request,
        "item/item_form.html",
        context={
            "game": game,
            "form": form,
            "links": [links.game_dashboard(game_pk)],
        },
    )


@login_required
def edit_item(request, item_pk):
    item = get_object_or_404(models.Item, pk=item_pk, game__created_by=request.user)
    form = forms.ItemForm(
        request.POST or None,
        game_pk=item.game.pk,
        initial={
            "name": item.name,
            "accepted_names": item.accepted_names,
            "description": item.description,
            "in_room_description": item.in_room_description,
            "item_type": item.item_type,
            "room": item.room,
            "can_be_taken": item.can_be_taken,
            "contained_within": item.contained_within,
            "is_starting_item": item.is_starting_item,
            **(
                {
                    "min_damage": item.damage.min_damage if item.damage else 0,
                    "max_damage": item.damage.max_damage if item.damage else 0,
                } 
                if item.item_type == models.Item.ItemTypeChoices.WEAPON
                else {}
            )
        },
    )

    if request.method == "POST" and form.is_valid():
        item.name = form.cleaned_data["name"]
        item.accepted_names = form.cleaned_data["accepted_names"]
        item.description = form.cleaned_data["description"]
        item.in_room_description = form.cleaned_data["in_room_description"]
        item.item_type = form.cleaned_data["item_type"]
        item.room = form.cleaned_data["room"]
        item.can_be_taken = form.cleaned_data["can_be_taken"]
        item.contained_within = form.cleaned_data["contained_within"]
        item.is_starting_item = form.cleaned_data["is_starting_item"]
        item.save()
        if item.item_type == models.Item.ItemTypeChoices.WEAPON:
            damage = item.damage
            damage.min_damage = form.cleaned_data["min_damage"]
            damage.max_damage = form.cleaned_data["max_damage"]


        return helpers.custom_redirect(
            "game:dashboard", kwargs={"game_pk": item.game.pk}
        )

    return render(
        request,
        "item/item_form.html",
        context={
            "editing": True,
            "form": form,
            "links": [links.game_dashboard(item.game.pk)],
        },
    )


@login_required
def delete_item(request, item_pk):
    item = get_object_or_404(models.Item, pk=item_pk, game__created_by=request.user)
    game_pk = item.game.pk
    item.delete()
    return helpers.custom_redirect("game:dashboard", kwargs={"game_pk": item.game.pk})
