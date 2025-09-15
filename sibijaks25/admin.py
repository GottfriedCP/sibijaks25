from django.contrib import admin
from .models import Banner, Naskah


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass


@admin.register(Naskah)
class NaskahAdmin(admin.ModelAdmin):
    list_display = ("judul", "peserta", "date_created")
    search_fields = ("judul", "peserta__nama", "peserta__email")
    list_filter = ("jenis_naskah", "date_created")
    ordering = ("-date_created",)
