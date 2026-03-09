from django.http import HttpResponseRedirect
from django.shortcuts import reverse


def custom_redirect(viewname, kwargs=None):
    return HttpResponseRedirect(reverse(viewname, kwargs=kwargs))


def redirect_to_game_dashboard(game_pk):
    return custom_redirect("game:dashboard", kwargs={"game_pk": game_pk})
