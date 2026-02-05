from django.urls import path

from . import views

app_name = "room"

urlpatterns = [
    path("new/<int:game_pk>/", views.create_room, name="new"),
    path("edit/<int:room_pk>/", views.edit_room, name="edit"),
    path(
        "set_starting/<int:room_pk>/", views.set_as_starting_room, name="set_starting"
    ),
    path("delete/<int:room_pk>/", views.delete_room, name="delete"),
    path("new_exit/<int:game_pk>/", views.create_exit, name="new_exit"),
    path("edit_exit/<int:game_pk>/<int:exit_pk>/", views.edit_exit, name="edit_exit"),
    path("delete_exit/<int:exit_pk>/", views.delete_exit, name="delete_exit"),
]
