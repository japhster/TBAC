from django.http import HttpResponseRedirect
from django.shortcuts import reverse


def custom_redirect(viewname, kwargs=None):
    return HttpResponseRedirect(reverse(viewname, kwargs=kwargs))
