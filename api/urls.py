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
    path(
        "play/fight/<int:session_pk>/",
        api.perform_attack_round,
        name="perform_attack_round",
    ),
    path(
        "play/fight/enemies/<int:session_pk>/",
        api.get_enemy_table_data,
        name="get_enemy_table_data",
    ),
    path(
        "play/fight/player/<int:session_pk>/",
        api.get_player_table_data,
        name="get_player_table_data",
    ),
]
