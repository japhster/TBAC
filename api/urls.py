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
    # network apis
    path(
        "network/data/<int:game_pk>/",
        api.get_network_data,
        name="get_network_data",
    ),
    path(
        "network/node/add/<int:game_pk>/",
        api.add_new_node,
        name="add_node",
    ),
    path(
        "network/edge/add/<int:game_pk>/",
        api.add_new_edge,
        name="add_edge",
    ),
    path(
        "network/node/delete/<int:node_pk>/",
        api.delete_node,
        name="delete_node",
    ),
    path(
        "network/edge/delete/<int:edge_pk>/",
        api.delete_edge,
        name="delete_edge",
    ),
    path(
        "network/node/update/<int:node_pk>/",
        api.update_node,
        name="update_node",
    ),
    path(
        "network/node/data/<int:node_pk>/",
        api.get_node_data,
        name="node_data",
    ),
    path(
        "network/edge/update/<int:edge_pk>/",
        api.update_edge,
        name="update_edge",
    ),
    path(
        "network/edge/data/<int:edge_pk>/",
        api.get_edge_data,
        name="edge_data",
    ),
]
