from django.urls import path

from . import views, views_panitia

app_name = "sibijaks25"
urlpatterns = [
    path("", views.index, name="index"),
    path("registrasi/", views.registrasi, name="registrasi"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("naskah/", views.naskah, name="naskah"),
    # path("naskah/<int:id>/edit/", views.edit_naskah, name="edit_naskah"),
    # path("naskah/<int:id>/hapus/", views.hapus_naskah, name="hapus_naskah"),
    path("naskah/<int:id>/", views.detail_naskah, name="detail_naskah"),
    path("naskah-baru/", views.tambah_naskah, name="tambah_naskah"),
    path("kolaborator/", views.kolaborator, name="kolaborator"),
    path("kolaborator/<int:id>/edit/", views.edit_kolaborator, name="edit_kolaborator"),
    path("kolaborator-baru/", views.tambah_kolaborator, name="tambah_kolaborator"),
    path("unggah-foto/<int:peserta_id>/", views.unggah_foto, name="unggah_foto"),
    # PANITIA
    path(
        "panitia/naskah/<int:id>/",
        views_panitia.detail_naskah,
        name="panitia_detail_naskah",
    ),
    path("panitia/naskah/", views_panitia.naskah, name="panitia_naskah"),
    # simpan penilaian skrining naskah
    path(
        "panitia/simpan-penilaian/",
        views_panitia.simpan_penilaian,
        name="simpan_penilaian",
    ),
    # simpan juri naskah
    path("panitia/simpan-juri/", views_panitia.simpan_juri, name="simpan_juri"),
    path("login-panitia/", views_panitia.login_panitia_view, name="login_panitia"),
]
