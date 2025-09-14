from django.urls import path

from . import views

app_name = "sibijaks25"
urlpatterns = [
    path("", views.index, name="index"),
    path("registrasi/", views.registrasi, name="registrasi"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("naskah/", views.naskah, name="naskah"),
    path("naskah-baru/", views.tambah_naskah, name="tambah_naskah"),
]
