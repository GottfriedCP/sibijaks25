from django.db import models


class ASN(models.Model):
    jenis = models.CharField(max_length=5, db_comment="pns atau pppk")
    nama = models.CharField(max_length=200)
    nip = models.CharField(unique=True, max_length=18)
    pangkat = models.CharField(max_length=50, blank=True, null=True)
    golongan = models.CharField(max_length=5, blank=True, null=True)
    tempat_lahir = models.CharField(max_length=50, blank=True, null=True)
    tanggal_lahir = models.DateField(blank=True, null=True)
    jabatan = models.CharField(max_length=100, blank=True, null=True)
    tmt_asn = models.IntegerField(blank=True, null=True, db_comment="tmt cpns/cpppk")
    # 0 = staf, 1 = katim, 2 = es 2, 3 = es 1, dst
    level = models.SmallIntegerField(blank=True, null=True)
    nomor_timker = models.SmallIntegerField(blank=True, null=True)
    aktif = models.BooleanField()

    class Meta:
        # explicit app label, remove if part of app.
        app_label = "master"
        managed = False
        db_table = "asn"


class PPNPN(models.Model):
    nomor_induk = models.CharField(unique=True, max_length=25)
    nama = models.CharField(max_length=150)
    nomor_timker = models.SmallIntegerField(blank=True, null=True)
    aktif = models.BooleanField()

    class Meta:
        # explicit app label, remove if part of app.
        app_label = "master"
        managed = False
        db_table = "ppnpn"


class Timker(models.Model):
    nomor_timker = models.SmallIntegerField()
    nama_timker = models.CharField(max_length=300)
    unit_kerja = models.CharField(max_length=500)

    class Meta:
        # explicit app label, remove if part of app.
        app_label = "master"
        managed = False
        db_table = "timker"
        unique_together = (("nomor_timker", "unit_kerja"),)

    def __str__(self):
        return f"Timker {self.nomor_timker} - {self.nama_timker}"
