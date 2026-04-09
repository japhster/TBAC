from django.urls import path

from . import views

app_name = "npc"

urlpatterns = [
    # friend urls
    path("friend/detail/<int:friend_pk>", views.friend_detail, name="friend"),
    path("friend/new/<int:game_pk>/", views.create_friend, name="new_friend"),
    path("friend/edit/<int:friend_pk>/", views.edit_friend, name="edit_friend"),
    path("friend/delete/<int:friend_pk>/", views.delete_friend, name="delete_friend"),
    path(
        "friend/<int:friend_pk>/accepted_items/add/",
        views.add_accepted_item_to_friend,
        name="add_accepted_item",
    ),
    path(
        "friend/accepted_items/edit/<int:accepted_item_pk>/",
        views.edit_accepted_item,
        name="edit_accepted_item",
    ),
    # enemy urls
    path("enemy/detail/<int:enemy_pk>", views.enemy_detail, name="enemy"),
    path("enemy/new/<int:game_pk>/", views.create_enemy, name="new_enemy"),
    path("enemy/edit/<int:enemy_pk>/", views.edit_enemy, name="edit_enemy"),
    path("enemy/delete/<int:enemy_pk>/", views.delete_enemy, name="delete_enemy"),
    path("enemy/drop/add/<int:enemy_pk>/", views.add_drop_to_enemy, name="add_drop"),
    path(
        "enemy/drop/remove/<int:drop_pk>/",
        views.remove_drop_from_enemy,
        name="remove_drop",
    ),
    # dialogue urls
    path("dialogue/list/<int:friend_pk>/", views.dialogue_list, name="dialogue_list"),
    path("dialogue/detail/<int:dialogue_pk>/", views.dialogue_detail, name="dialogue"),
    path("dialogue/new/<int:friend_pk>/", views.create_dialogue, name="new_dialogue"),
    path(
        "dialogue/new/response/<int:parent_pk>/",
        views.create_dialogue,
        name="new_response",
    ),
    path(
        "dialogue/edit/<int:dialogue_pk>/",
        views.edit_dialogue,
        name="edit_dialogue",
    ),
    path(
        "dialogue/gift/add/<int:dialogue_pk>/",
        views.add_gift_to_dialogue,
        name="add_gift",
    ),
    path(
        "dialogue/gift/remove/<int:gift_pk>/",
        views.remove_gift_from_dialogue,
        name="remove_gift",
    ),
    path(
        "dialogue/<int:dialogue_pk>/hide/",
        views.hide_dialogue,
        name="hide_dialogue",
    ),
    path(
        "dialogue/<int:dialogue_pk>/show/",
        views.show_dialogue,
        name="show_dialogue",
    ),
]
