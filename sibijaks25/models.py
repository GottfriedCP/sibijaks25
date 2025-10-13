from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
import os
import uuid


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


def validate_abstrak_pdf(file):
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Ukuran file abstrak maksimal 5MB.")
    if hasattr(file, "content_type"):
        if file.content_type != "application/pdf":
            raise ValidationError("File abstrak harus berupa PDF.")
    else:
        ext = os.path.splitext(file.name)[1].lower()
        if ext != ".pdf":
            raise ValidationError("File abstrak harus berupa PDF.")


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


class Countdown(TimestampedModel):
    judul = models.CharField(max_length=255)
    kode = models.TextField(help_text="Kode HTML/JS untuk countdown timer.")
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.judul


class Peserta(TimestampedModel):
    MAHASISWA_CHOICES = {
        "d3": "D3",
        "s1": "D4 / S1",
        "s2": "S2 / pasca sarjana",
        "s3": "S3 / post doktoral",
    }
    PENDIDIKAN_CHOICES = [
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
    is_mahasiswa = models.BooleanField(
        verbose_name="Saya ingin mendaftar kompetisi ini sebagai mahasiswa",
        default=False,
    )
    mahasiswa = models.CharField(
        verbose_name="Mahasiswa jenjang",
        choices=MAHASISWA_CHOICES,
        max_length=3,
        blank=True,
        null=True,
    )
    institusi = models.CharField(
        max_length=500,
        help_text="Jika Anda mendaftar sebagai mahasiswa, tuliskan nama perguruan tinggi.",
    )
    pekerjaan_ht = f'Jika Anda mahasiswa, isikan "Mahasiswa"'
    pekerjaan = models.CharField(
        verbose_name="Profesi/Pekerjaan/Jabatan",
        # help_text=pekerjaan_ht,
        max_length=255,
        blank=True,
        null=True,
    )
    pendidikan = models.CharField(
        max_length=5,
        choices=PENDIDIKAN_CHOICES,
        verbose_name="Pendidikan Terakhir",
        blank=True,
        null=True,
        help_text="Kosongkan jika tidak relevan",
    )
    pasfoto_ht = "Upload pasfoto formal dengan latar belakang merah, rasio 2x3, ukuran maksimal 2 MB."
    pasfoto = models.ImageField(
        max_length=500,
        upload_to="pasfoto/",
        blank=True,
        null=True,
        help_text=pasfoto_ht,
        validators=[validate_pasfoto],
    )

    class Meta:
        verbose_name_plural = "Peserta"

    def __str__(self):
        return self.nama


class Kolaborator(TimestampedModel):
    PENDIDIKAN_CHOICES = Peserta.PENDIDIKAN_CHOICES
    peserta = models.ForeignKey(
        Peserta, on_delete=models.CASCADE, related_name="kolaborators"
    )
    nama = models.CharField(
        max_length=500,
        help_text="Nama lengkap sesuai KTP atau identitas resmi lainnya.",
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    nomor_wa = models.CharField(
        verbose_name="Nomor WA",
        max_length=20,
        # validators=[MinLengthValidator(5, message="Nomor WA minimal 5 karakter.")],
        blank=True,
        null=True,
    )
    institusi_ht = "Minimal satu kolaborator harus berasal dari institusi yang berbeda dengan ketua tim atau penulis utama."
    institusi = models.CharField(max_length=500, help_text=institusi_ht)
    pendidikan = models.CharField(
        max_length=5,
        choices=PENDIDIKAN_CHOICES,
        verbose_name="Pendidikan Terakhir",
        blank=True,
        null=True,
        help_text="Kosongkan jika tidak relevan",
    )
    pekerjaan_ht = f'Jika mahasiswa, tuliskan "Mahasiswa"'
    pekerjaan = models.CharField(
        help_text=pekerjaan_ht,
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.nama} - {self.institusi}"


def konsep_dir_path(instance, filename):
    return f"konsep/{instance.JENIS_NASKAH_CHOICES.get(instance.jenis_naskah)}_{instance.judul}.pdf"


def naskah_dir_path(instance, filename):
    return f"naskah/{instance.JENIS_NASKAH_CHOICES.get(instance.jenis_naskah)}_{instance.judul}.pdf"


class Naskah(TimestampedModel):
    # tetap 100 mainly for now
    STATUS_NASKAH_CHOICES = [
        (100, "Terunggah"),
        (200, "Lolos Konsep"),
        (300, "Lolos Admin 2"),
        (666, "Gugur"),
    ]
    ARTIKEL_ILMIAH = "art"
    POLICY_BRIEF = "pb"
    JENIS_NASKAH_CHOICES = {
        ARTIKEL_ILMIAH: "Artikel Ilmiah",
        POLICY_BRIEF: "Policy Brief",
    }
    peserta = models.ForeignKey(
        Peserta, on_delete=models.CASCADE, related_name="naskahs"
    )
    judul = models.CharField(max_length=500)
    jenis_naskah = models.CharField(
        max_length=5,
        choices=JENIS_NASKAH_CHOICES,
        default="art",
        verbose_name="Jenis Naskah",
    )
    abstrak = models.TextField(
        verbose_name="Konsep",
        help_text="Maksimal konsep 400 kata (Policy Brief), 1150 kata (Artikel Ilmiah).",
    )
    file_abstrak_ht = "Unggah file konsep dalam format PDF, ukuran maksimal 5 MB."
    file_abstrak = models.FileField(
        verbose_name="File Konsep",
        upload_to=konsep_dir_path,
        help_text=file_abstrak_ht,
        max_length=500,
        blank=True,
        null=True,
        validators=[validate_abstrak_pdf],
    )
    naskah_ht = "Unggah naskah dalam format PDF, ukuran maksimal 20 MB."
    naskah = models.FileField(
        upload_to=naskah_dir_path,
        help_text=naskah_ht,
        max_length=500,
        blank=True,
        null=True,
    )
    kolaborators = models.ManyToManyField(
        Kolaborator,
        verbose_name="Kolaborator",
        help_text="Minimal satu orang harus dipilih.",
    )
    verified = models.BooleanField(default=False)
    verifier1 = models.CharField(max_length=255, blank=True, null=True)
    verifier2 = models.CharField(max_length=255, blank=True, null=True)
    status_naskah = models.IntegerField(
        choices=STATUS_NASKAH_CHOICES, default=100, verbose_name="Status Naskah"
    )
    # Variabel skrining
    s1 = models.BooleanField(default=False)
    s2 = models.BooleanField(default=False)
    s3 = models.BooleanField(default=False)
    s4 = models.BooleanField(default=False)
    s5 = models.BooleanField(default=False)
    komentar1 = models.TextField(blank=True, null=True)
    komentar2 = models.TextField(blank=True, null=True)
    juris = models.ManyToManyField(
        "Juri",
        through="Review2",
        related_name="naskahs",
        verbose_name="Reviewer",
        blank=True,
        # help_text='Juri yang melakukan review tahap 2 untuk naskah ini.',
    )

    class Meta:
        verbose_name_plural = "Naskah"

    def __str__(self):
        return f"{self.peserta.nama} - {self.judul}"


class Juri(TimestampedModel):
    """
    - `is_panitia` adalah juri yang juga panitia.
    - `is_supersubstansi` adalah juri substansi senior.
    """

    TAHAP_CHOICES = [
        (1, "Tahap 1"),
        (2, "Tahap 2"),
        (3, "Tahap 3"),
    ]
    ARTIKEL_ILMIAH = "art"
    POLICY_BRIEF = "pb"
    AI_PB = "artpb"
    JENIS_NASKAH_CHOICES = {
        ARTIKEL_ILMIAH: "AI",
        POLICY_BRIEF: "PB",
        AI_PB: "AI/PB",
    }
    nama = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    nomor_wa = models.CharField(
        verbose_name="Nomor WA",
        unique=True,
        max_length=20,
        # validators=[MinLengthValidator(5, message="Nomor WA minimal 5 karakter.")],
    )
    institusi = models.CharField(max_length=500, blank=True, null=True)
    pekerjaan = models.CharField(max_length=255, blank=True, null=True)
    # flag untuk show/hide informasi tertentu
    is_panitia = models.BooleanField(default=False)
    is_supersubstansi = models.BooleanField(default=False)
    tahap = models.IntegerField(choices=TAHAP_CHOICES, default=1)
    jenis_naskah = models.CharField(
        max_length=10,
        choices=JENIS_NASKAH_CHOICES,
        default=AI_PB,
        help_text="Jenis naskah yang diberikan untuk di-review oleh juri ini.",
    )

    class Meta:
        verbose_name_plural = "Juri"

    def __str__(self):
        return f"{self.nama} - ({self.JENIS_NASKAH_CHOICES.get(self.jenis_naskah)})"


class Review1(TimestampedModel):
    """Review1 (Review 1) adalah skrining menuju reviewer."""

    juri = models.ForeignKey(Juri, on_delete=models.CASCADE, related_name="reviews1")
    naskah = models.ForeignKey(
        Naskah, on_delete=models.CASCADE, related_name="reviews1"
    )
    s1 = models.BooleanField(default=False)
    s2 = models.BooleanField(default=False)
    s3 = models.BooleanField(default=False)
    s4 = models.BooleanField(default=False)
    s5 = models.BooleanField(default=False)
    s6 = models.BooleanField(default=False)
    komentar = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("juri", "naskah")
        verbose_name = "Review 1"
        verbose_name_plural = "Review 1"

    def __str__(self):
        return f"Review {self.juri.nama} - {self.naskah.judul}"


class Review2(TimestampedModel):
    """Review2 (Review 2) adalah review melibatkan eksternal."""

    juri = models.ForeignKey(Juri, on_delete=models.CASCADE, related_name="reviews2")
    naskah = models.ForeignKey(
        Naskah, on_delete=models.CASCADE, related_name="reviews2"
    )
    s1 = models.IntegerField(default=0)
    s2 = models.IntegerField(default=0)
    s3 = models.IntegerField(default=0)
    s4 = models.IntegerField(default=0)
    s5 = models.IntegerField(default=0)
    s6 = models.IntegerField(default=0)
    komentar = models.TextField(blank=True, null=True)
    total = models.IntegerField(default=0)
    lanjut = models.BooleanField(default=False)

    class Meta:
        unique_together = ("juri", "naskah")
        verbose_name = "Review 2"
        verbose_name_plural = "Review 2"

    def __str__(self):
        return f"Review {self.juri.nama} - {self.naskah.judul}"

    def save(self, *args, **kwargs):
        self.total = self.s1 + self.s2 + self.s3 + self.s4 + self.s5 + self.s6
        super().save(*args, **kwargs)
