from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL + "?next=/")