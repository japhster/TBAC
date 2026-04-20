from django.shortcuts import render, reverse
from .. import constants, docs_content


def docs_list(request):
    return render(
        request,
        "game/docs/list.html",
        context={
            "pages": [
                ("Playing a Text-Based Adventure", reverse("game:docs_playing")),
                ("Creating a Text-Based Adventure", reverse("game:docs_creating_home")),
            ]
        },
    )


def playing_documentation(request):
    return render(
        request,
        "game/docs/playing.html",
        context={
            "content": docs_content.PLAYING_SECTIONS,
        },
    )


def creating_documentation_home(request):
    return render(
        request,
        "game/docs/creating/home.html",
        context={
            "content": [
                ("ROOMS", "Rooms", "game/docs/creating/rooms.html"),
                ("ITEMS", "Items", "game/docs/creating/items.html"),
                ("FRIENDS", "Friends", "game/docs/creating/friends.html"),
                ("ENEMIES", "Enemies", "game/docs/creating/enemies.html"),
                ("ENDSTATES", "End States", "game/docs/creating/endstates.html"),
            ]
        },
    )
