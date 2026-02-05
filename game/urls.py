from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    path("list/", views.game_list, name="list"),
    path("detail/<int:game_pk>/", views.game_detail, name="detail"),
    path("detail/<int:game_pk>/<int:room_pk>/", views.game_detail, name="detail"),
    path("create/", views.create_game, name="new"),
    path("edit/<int:game_pk>/", views.edit_game, name="edit"),
    path("dashboard/<int:game_pk>/", views.game_dashboard, name="dashboard"),
]
