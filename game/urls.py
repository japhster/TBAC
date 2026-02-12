from django.urls import path

from . import session_views, views

app_name = "game"

urlpatterns = [
    path("list/", views.game_list, name="list"),
    path("detail/<int:game_pk>/", views.game_detail, name="detail"),
    path("create/", views.create_game, name="new"),
    path("edit/<int:game_pk>/", views.edit_game, name="edit"),
    path("dashboard/<int:game_pk>/", views.game_dashboard, name="dashboard"),
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
        "session/new/<int:game_pk>/",
        session_views.start_new_session,
        name="new_session",
    ),
    path("session/play/<int:session_pk>/", session_views.play_game, name="play"),
    path(
        "session/move/<int:session_pk>/<int:room_pk>/",
        session_views.move_room,
        name="move",
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
]
