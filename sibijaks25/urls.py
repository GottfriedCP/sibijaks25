from django.urls import path

from . import views

app_name = "sibijaks25"
urlpatterns = [
    path("", views.index, name="index"),
]
