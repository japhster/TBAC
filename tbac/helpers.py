from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from . import constants

def custom_redirect(viewname, kwargs=None):
    return HttpResponseRedirect(reverse(viewname, kwargs=kwargs))


def redirect_to_game_dashboard(game_pk):
    return custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})

def strip_stop_words(text):
    if isinstance(text, str):
        text = text.split()

    if not isinstance(text, list):
        raise TypeError("text arg must be either 'list' or 'str' types")

    return " ".join(word for word in text if word not in constants.STOP_WORDS)
