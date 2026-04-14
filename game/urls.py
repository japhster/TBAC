from django.urls import path

from . import session_views, views

app_name = "game"

urlpatterns = [
    path("list/", views.game_list, name="list"),
    path("my-games/", views.my_games, name="my_games"),
    path("create/", views.create_game, name="new"),
    path("edit/<int:game_pk>/", views.edit_game, name="edit"),
    # dashboard urls
    path("dashboard/<int:game_pk>/", views.game_dashboard, name="dashboard"),
    path("publish/<int:game_pk>/", views.publish_game, name="publish"),
    path("unpublish/<int:game_pk>/", views.unpublish_game, name="unpublish"),
    path("new/end_state/<int:game_pk>/", views.new_end_state, name="new_end_state"),
    path(
        "edit/end_state/<int:end_state_pk>", views.edit_end_state, name="edit_end_state"
    ),
    path(
        "delete/end_state/<int:end_state_pk>",
        views.delete_end_state,
        name="delete_end_state",
    ),
    # session urls
    path(
        "session/start/<int:game_pk>/",
        session_views.start_session,
        name="start_session",
    ),
    path(
        "session/new/<int:game_pk>/",
        session_views.start_new_session,
        name="new_session",
    ),
    path("session/play/<int:session_pk>/", session_views.play_game, name="play"),
    path(
        "session/play/<int:session_pk>/interpret/",
        session_views.interpret_command,
        name="interpreter",
    ),
    path(
        "session/move/<int:session_pk>/<int:room_pk>/",
        session_views.move_room,
        name="move",
    ),
    path(
        "session/leave/<int:session_pk>/",
        session_views.leave_room,
        name="leave",
    ),
    path(
        "session/take/<int:session_pk>/<int:item_pk>/",
        session_views.take_item,
        name="take",
    ),
    path(
        "session/open/<int:session_pk>/<int:item_pk>/",
        session_views.open_item,
        name="open",
    ),
    path(
        "session/use/<int:session_pk>/<int:item_pk>/",
        session_views.use_item,
        name="use",
    ),
    path(
        "session/inspect/<int:session_pk>/<int:item_pk>/",
        session_views.inspect_item,
        name="inspect",
    ),
    path(
        "session/fight/<int:session_pk>/<int:enemy_pk>/",
        session_views.fight_enemy,
        name="fight",
    ),
    path(
        "session/attack/<int:session_pk>/<int:enemy_pk>/<int:attack_pk>/",
        session_views.attack_enemy,
        name="attack",
    ),
    path(
        "session/enemy_attack/<int:session_pk>/<int:enemy_pk>/",
        session_views.enemy_attack,
        name="enemy_attack",
    ),
    path(
        "session/fight/<int:session_pk>/<int:enemy_pk>/success/",
        session_views.fight_won,
        name="fight_won",
    ),
    path(
        "session/talk/<int:session_pk>/<int:friend_pk>/",
        session_views.talk_to_friend,
        name="talk",
    ),
    path(
        "session/discussion/<int:session_pk>/<int:dialogue_pk>/",
        session_views.friend_discussion,
        name="discussion",
    ),
    path(
        "session/give/<int:session_pk>/<int:accepted_item_pk>/",
        session_views.give_item_to_friend,
        name="give",
    ),
]
