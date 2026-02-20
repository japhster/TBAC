from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render

from . import forms


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL + "?next=/")


def login_view(request):
    form = forms.LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is not None:
            login(request, user)
            redirect_link = request.GET.get("next")
            if redirect_link is not None:
                return HttpResponseRedirect(redirect_link)

            return redirect("game:list")
        else:
            form.add_error(
                "password",
                ValidationError({"password": "There was an error logging you in."}),
            )

    return render(request, "login.html", context={"form": form})
