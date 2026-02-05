from django.shortcuts import reverse

game_dashboard = lambda pk: (
    "back to dashboard",
    reverse("game:dashboard", kwargs={"game_pk": pk}),
)
