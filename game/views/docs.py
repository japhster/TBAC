from django.shortcuts import render, reverse
from .. import constants

def docs_list(request):
    return render(
        request,
        "game/docs/list.html",
        context={
            "pages": [
                ("Playing a Text-Based Adventure", reverse("game:docs_playing")),
                ("Creating a Text-Based Adventure", reverse("game:docs_creating_home")),
            ]
        }
    )


def playing_documentation(request):
    return render(
        request,
        "game/docs/playing.html",
        context={
            "commands": constants.COMMAND_OPTIONS,
        }
    )


def creating_documentation_home(request):
    return render(
        request,
        "game/docs/creating_home.html",
    )

