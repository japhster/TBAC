from django.urls import path

from . import api

app_name = "api"

urlpatterns = [
    # API URLS
    path(
        "game/name/<int:game_pk>/",
        api.get_game_name,
        name="get_game_name",
    ),
    path(
        "game/update/name/<int:game_pk>/",
        api.update_game_name,
        name="update_game_name",
    ),
    path(
        "exit/add/<int:room_pk>/",
        api.add_exit_to_room,
        name="add_exit_to_room",
    ),
    path(
        "exit/list/<int:game_pk>/",
        api.get_exit_data,
        name="get_exit_data",
    ),
]
