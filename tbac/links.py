from django.shortcuts import reverse

game_dashboard = lambda pk, hashtag=None: (
    "back to dashboard",
    (
        reverse("game:dashboard", kwargs={"game_pk": pk})
        + (f"#{hashtag}" if hashtag is not None else "")
    ),
)
