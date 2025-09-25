from django.contrib import admin
from .models import Banner, Countdown, Juri, Peserta, Naskah, Review1


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("judul", "aktif")


@admin.register(Countdown)
class CountdownAdmin(admin.ModelAdmin):
    list_display = ("judul", "aktif")


@admin.register(Naskah)
class NaskahAdmin(admin.ModelAdmin):
    list_display = ("judul", "peserta", "date_created")
    search_fields = ("judul", "peserta__nama", "peserta__email")
    list_filter = ("jenis_naskah", "date_created")
    ordering = ("-date_created",)


@admin.register(Peserta)
class PesertaAdmin(admin.ModelAdmin):
    list_display = ("nama", "email", "nomor_wa", "institusi", "is_mahasiswa")
    search_fields = ("nama", "email", "nomor_wa", "institusi")
    list_filter = ("is_mahasiswa", "pendidikan")
    ordering = ("nama",)


@admin.register(Juri)
class JuriAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "email",
        "nomor_wa",
        "institusi",
        "is_panitia",
        "is_supersubstansi",
        "tahap",
    )
    search_fields = ("nama", "email", "nomor_wa", "institusi")
    list_filter = ("tahap",)
    ordering = ("nama",)


@admin.register(Review1)
class Review1Admin(admin.ModelAdmin):
    list_display = (
        "juri",
        "naskah",
        "s1",
        "s2",
        "s3",
        "s4",
        "s5",
        "s6",
        "date_created",
    )
    search_fields = ("juri__nama", "naskah__judul", "naskah__peserta__nama")
    list_filter = ("s1", "s2", "s3", "s4", "s5", "s6", "date_created")
    ordering = ("-date_created",)
