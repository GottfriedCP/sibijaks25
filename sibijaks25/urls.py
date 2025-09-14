from django.urls import path

from . import views

app_name = "sibijaks25"
urlpatterns = [
    path("", views.index, name="index"),
    path("registrasi/", views.registrasi, name="registrasi"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("naskah/", views.naskah, name="naskah"),
    path("naskah/<int:id>/edit/", views.edit_naskah, name="edit_naskah"),
    path("naskah-baru/", views.tambah_naskah, name="tambah_naskah"),
    path("kolaborator/", views.kolaborator, name="kolaborator"),
    path("kolaborator/<int:id>/edit/", views.edit_kolaborator, name="edit_kolaborator"),
    path("kolaborator-baru/", views.tambah_kolaborator, name="tambah_kolaborator"),
]
