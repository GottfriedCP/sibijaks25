from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
import os


def validate_pasfoto(image):
    # Check file size (2MB = 2 * 1024 * 1024 bytes)
    if image.size > 2 * 1024 * 1024:
        raise ValidationError("Ukuran pasfoto maksimal 2MB.")
    # Check file type
    valid_mime_types = ["image/jpeg", "image/png"]
    if hasattr(image, "content_type"):
        if image.content_type not in valid_mime_types:
            raise ValidationError("Pasfoto harus berupa file PNG atau JPEG.")
    else:
        # Fallback: check extension if content_type is not available
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            raise ValidationError("Pasfoto harus berupa file PNG atau JPEG.")


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


class Peserta(TimestampedModel):
    pendidikan_choices = [
        ("d3", "D3"),
        ("s1", "D4 / S1"),
        ("s2", "S2"),
        ("s3", "S3"),
    ]
    nama = models.CharField(
        max_length=255,
        help_text="Nama lengkap sesuai KTP atau identitas resmi lainnya.",
    )
    email = models.EmailField(
        unique=True,
        help_text="Email nantinya akan digunakan untuk login ke situs web ini.",
    )
    nomor_wa = models.CharField(
        verbose_name="Nomor WA",
        unique=True,
        max_length=20,
        # validators=[MinLengthValidator(5, message="Nomor WA minimal 5 karakter.")],
        help_text="Nomor WA nantinya akan digunakan untuk login ke situs web ini.",
    )
    institusi = models.CharField(max_length=500)
    # mahasiswa = models.BooleanField(verbose_name="Apakah Anda berstatus mahasiswa?", default=False)
    pekerjaan_ht = f'Jika Anda mahasiswa, isikan "Mahasiswa"'
    pekerjaan = models.CharField(
        verbose_name="Profesi/Pekerjaan/Jabatan", help_text=pekerjaan_ht, max_length=255
    )
    pendidikan = models.CharField(
        max_length=5, choices=pendidikan_choices, verbose_name="Pendidikan Terakhir"
    )
    pasfoto_ht = "Upload pasfoto formal dengan latar belakang merah, rasio 2x3, ukuran maksimal 2MB."

    pasfoto = models.ImageField(
        max_length=500,
        upload_to="pasfoto/",
        blank=True,
        null=True,
        help_text=pasfoto_ht,
        validators=[validate_pasfoto],
    )

    def __str__(self):
        return self.nama


class Kolaborator(TimestampedModel):
    peserta = models.ForeignKey(
        Peserta, on_delete=models.CASCADE, related_name="kolaborators"
    )
    nama = models.CharField(
        max_length=500,
        help_text="Nama lengkap sesuai KTP atau identitas resmi lainnya.",
    )
    institusi_ht = "Institusi harus berbeda dengan ketua tim / penulis utama."
    institusi = models.CharField(max_length=500, help_text=institusi_ht)

    def __str__(self):
        return f"{self.nama} - {self.institusi}"


class Naskah(TimestampedModel):
    peserta = models.ForeignKey(Peserta, on_delete=models.CASCADE, related_name="naskahs")
    judul = models.CharField(max_length=500)
    abstrak = models.TextField(verbose_name="Concept Proposal (Abstrak)", help_text="Maksimal 250 kata.")
    naskah_ht = "Unggah naskah dalam format PDF, ukuran maksimal 20 MB."
    naskah = models.FileField(
        upload_to="naskah/",
        help_text=naskah_ht,
        max_length=500,
        blank=True,
        null=True,
    )
    kolaborators = models.ManyToManyField(Kolaborator, verbose_name="Kolaborator", help_text="Minimal satu harus dipilih.")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.peserta.nama} - {self.judul}"
