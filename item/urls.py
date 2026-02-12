from django.urls import path

from . import views

app_name = "item"

urlpatterns = [
    path("new/<int:game_pk>/", views.create_item, name="new"),
    path("edit/<int:item_pk>/", views.edit_item, name="edit"),
    path("delete/<int:item_pk>/", views.delete_item, name="delete"),
]
