from django.db import models


class TimestampedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Banner(TimestampedModel):
    judul = models.CharField(max_length=255)
    gambar = models.ImageField(upload_to="banners/")
    link = models.URLField(blank=True, null=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.judul


# class Peserta(TimestampedModel):
#     nama = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     nomor_wa = models.CharField(max_length=20)

#     def __str__(self):
#         return self.nama
