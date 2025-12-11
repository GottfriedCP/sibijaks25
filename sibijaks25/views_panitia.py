from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .decorators import peserta_session_required, staff_required
from .forms import NaskahJuriForm
from .models import Banner, Juri, Naskah, Peserta, Review1, Review2

from decimal import Decimal, InvalidOperation

from environs import env
from openpyxl import Workbook

import os

env.read_env()


@login_required
@staff_required
def naskah(request):
    """laman daftar naskah untuk panitia."""
    juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
    pesertas = Peserta.objects.all()
    jumlah_tim = pesertas.count()
    # hitung jumlah tim yang sudah submit minimal 1 naskah
    jumlah_tim_dengan_naskah = pesertas.filter(naskahs__isnull=False).distinct().count()
    naskahs = (
        Naskah.objects.select_related("peserta").prefetch_related("kolaborators").all()
    )
    naskahs_list = []
    for n in naskahs:
        bisa_dinilai = not bool(n.verifier1)
        if juri.is_supersubstansi:
            bisa_dinilai = n.status_naskah != 666 and not bool(n.verifier2)
        jumlah_juri = n.juris.count()
        unggah_ft = "Sudah" if bool(n.naskah) else "Belum"
        naskahs_list.append((n, bisa_dinilai, jumlah_juri, unggah_ft))

    reviewers = (
        Juri.objects.filter(is_panitia=False)
        .prefetch_related("naskahs")
        .order_by("jenis_naskah", "nama")
    )
    reviewers_list = []
    for r in reviewers:
        jml_naskah_selesai = Review2.objects.filter(juri=r, total2__gt=0).count()
        jml_naskah = r.naskahs.count()
        selesai = "Ya" if jml_naskah_selesai == jml_naskah else "Belum"
        # perhitungkan juga reviewer yang menganggur
        selesai = "-" if jml_naskah == 0 else selesai
        reviewers_list.append((r, jml_naskah, jml_naskah_selesai, selesai))

    context = {
        "juri": juri,
        "jumlah_tim": jumlah_tim,
        "jumlah_tim_dengan_naskah": jumlah_tim_dengan_naskah,
        "jumlah_naskah": naskahs.count(),
        "jumlah_artikel": naskahs.filter(jenis_naskah=Naskah.ARTIKEL_ILMIAH).count(),
        "jumlah_artikel_lolos_skrining": naskahs.filter(
            jenis_naskah=Naskah.ARTIKEL_ILMIAH, verified=True
        )
        .exclude(status_naskah=666)
        .count(),
        "jumlah_pb": naskahs.filter(jenis_naskah=Naskah.POLICY_BRIEF).count(),
        "jumlah_pb_lolos_skrining": naskahs.filter(
            jenis_naskah=Naskah.POLICY_BRIEF, verified=True
        )
        .exclude(status_naskah=666)
        .count(),
        "naskahs": naskahs_list,
        "reviewers": reviewers_list,
    }
    return render(request, "sibijaks25/panitia/naskah.html", context)


@login_required
@staff_required
def simpan_penilaian(request):
    if request.method == "POST":
        juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
        id_naskah = request.POST.get("id_naskah")
        naskah = get_object_or_404(Naskah, id=id_naskah)
        # form data
        naskah.s1 = request.POST.get("s1") == "1"
        naskah.s2 = request.POST.get("s2") == "1"
        naskah.s3 = request.POST.get("s3") == "1"
        print(naskah.s1)
        print(request.POST.get("s1"))
        if juri.is_supersubstansi:
            naskah.s4 = request.POST.get("s4") == "1"
            naskah.s5 = request.POST.get("s5") == "1"
            naskah.komentar2 = request.POST.get("k", "").strip()
        naskah.komentar1 = request.POST.get("k", "").strip()
        if juri.is_supersubstansi:
            if naskah.verifier2:
                messages.error(
                    request,
                    f"Naskah berjudul '{naskah.judul}' baru saja dinilai oleh {naskah.verifier2}.",
                )
                return redirect("sibijaks25:panitia_detail_naskah", id=naskah.id)
            naskah.verifier2 = juri.nama
            naskah.verifier1 = juri.nama if not naskah.verifier1 else naskah.verifier1
        else:
            if naskah.verifier1 or naskah.verifier2:
                messages.error(
                    request, f"Naskah berjudul '{naskah.judul}' baru saja dinilai."
                )
                return redirect("sibijaks25:panitia_detail_naskah", id=naskah.id)
            naskah.verifier1 = juri.nama
        naskah.verified = True
        if juri.is_supersubstansi and not naskah.s5:
            naskah.status_naskah = 666  # gugur
        else:
            naskah.status_naskah = (
                naskah.status_naskah if all([naskah.s1, naskah.s2, naskah.s3]) else 666
            )
        naskah.save()
        messages.success(request, "Penilaian berhasil disimpan.")
    return redirect("sibijaks25:panitia_naskah")


@login_required
@staff_required
def simpan_juri(request):
    if request.method == "POST":
        juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
        # if not juri.is_supersubstansi:
        #     messages.error(request, "Hanya super substansi yang bisa mengubah juri.")
        #     return redirect("sibijaks25:panitia_naskah")
        id_naskah = request.POST.get("id_naskah")
        naskah = get_object_or_404(Naskah, id=id_naskah)
        form = NaskahJuriForm(request.POST, instance=naskah)
        if form.is_valid():
            form.save()
            messages.success(request, "Juri berhasil ditetapkan untuk naskah ini.")
        else:
            messages.error(request, "Gagal menyimpan juri.")
            return redirect("sibijaks25:panitia_detail_naskah", id=naskah.id)
    return redirect("sibijaks25:panitia_naskah")


@login_required
@staff_required
def detail_naskah(request, id):
    juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
    naskah = get_object_or_404(Naskah.objects.select_related("peserta"), id=id)
    ada_pasfoto = bool(getattr(naskah.peserta, "pasfoto", None))
    bisa_dinilai = not bool(naskah.verifier1)
    if juri.is_supersubstansi:
        bisa_dinilai = naskah.status_naskah != 666 and not bool(naskah.verifier2)
    reviewers = (
        Juri.objects.filter(is_panitia=False)
        .prefetch_related("naskahs")
        .order_by("nama")
    )
    reviewers_list = []
    for r in reviewers:
        jml_naskah_selesai = Review2.objects.filter(juri=r, total2__gt=0).count()
        jml_naskah = r.naskahs.count()
        reviewers_list.append((r, jml_naskah, jml_naskah_selesai))
    context = {
        "naskah": naskah,
        "juri": juri,
        "ada_pasfoto": ada_pasfoto,
        "bisa_dinilai": bisa_dinilai,
        "is_supersubstansi": juri.is_supersubstansi,
        "form_juri": (
            NaskahJuriForm(instance=naskah, rev_only=True)
            if juri.is_panitia and not naskah.status_naskah == 666
            else None
        ),
        "reviewers": reviewers_list,
    }
    return render(request, "sibijaks25/panitia/detail_naskah.html", context)


@login_required
@staff_required
def unduh_rekap(request):
    if request.method == "POST":
        JUMLAH_REVIEWER = 2
        wb = Workbook()
        ws = wb.active

        # Write headers
        headers = ["ID Naskah", "Jenis Naskah", "Judul"]
        headers.extend(["Ketua Tim", "Nomor WA", "Email"])
        headers.extend(["Mahasiswa", "Mahasiswa Jenjang", "Profesi", "Instansi"])
        headers.extend(["Status", "File Konsep", "Verifier 1", "Verifier 2"])
        headers.extend(["Meminta Data?", "Hasil Permintaan Data", "Full text"])
        # Reviewer Konsep
        headers.extend(["Selesai Review", "Nilai avg", "Predikat"])
        headers.extend(["Terlambat"])
        headers.extend([f"Reviewer 1", "Skor", "Komentar", "Rekomendasi"])
        headers.extend([f"Reviewer 2", "Skor", "Komentar", "Rekomendasi"])
        # headers.extend([f"Reviewer 3", "Skor", "Komentar", "Rekomendasi"])
        ws.append(headers)

        naskahs = Naskah.objects.select_related("peserta")
        naskahs = naskahs.prefetch_related("reviews2", "reviews2__juri")
        naskahs = naskahs.order_by("id")

        for naskah in naskahs:
            status = "Lolos skrining" if naskah.status_naskah != 666 else "Gugur"
            row = [naskah.id, naskah.get_jenis_naskah_display(), naskah.judul]
            is_mahasiswa = "Ya" if naskah.peserta.is_mahasiswa else "Bukan"
            row.extend(
                [
                    naskah.peserta.nama,
                    naskah.peserta.nomor_wa,
                    naskah.peserta.email,
                    is_mahasiswa,
                    naskah.peserta.get_mahasiswa_display() if is_mahasiswa else "-",
                    naskah.peserta.pekerjaan or "-",
                    naskah.peserta.institusi,
                ]
            )
            try:
                file_abstrak = str(os.path.basename(naskah.file_abstrak.name))
            except:
                file_abstrak = "-"
            row.extend([status, file_abstrak, naskah.verifier1, naskah.verifier2])
            row.extend(
                [
                    "Ya" if naskah.meminta_data else "",
                    "",
                    f"https://sibijaks.bkpk.kemkes.go.id{naskah.naskah.url}" if naskah.naskah else "",
                ]
            )
            # Reviewer Konsep (data), di-append ke row terakhiran
            total_nilai = 0
            selesai_semua = True
            list_detail_penilaian = []
            for r in naskah.reviews2.all():
                total_nilai += r.total2
                rekomendasi = "Lanjut"
                if r.total2 == 0:
                    selesai_semua = False
                    rekomendasi = "-"
                elif r.total2 > 0 and not r.lanjut:
                    rekomendasi = "Tidak lanjut"
                list_detail_penilaian.extend(
                    [
                        r.juri.nama,
                        "-" if r.total2 == 0 else r.total2,
                        r.komentar2 or "-",
                        rekomendasi,
                    ]
                )

            if naskah.status_naskah != 666 and selesai_semua:
                try:
                    nilai_avg = Decimal(total_nilai) / Decimal(naskah.reviews2.count())
                except InvalidOperation as e:
                    nilai_avg = Decimal(1)
                nilai_avg = nilai_avg.quantize(Decimal("0.00"))
                predikat = "Kurang Baik"
                if nilai_avg > Decimal(400):
                    predikat = "Sangat Baik"
                elif nilai_avg > Decimal(200):
                    predikat = "Baik"
                row.extend(["Sudah", nilai_avg, predikat])
            else:
                row.extend(["", "", ""])
            row.extend(["Ya" if naskah.terlambat else ""])
            row.extend(list_detail_penilaian)
            ws.append(row)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        now = timezone.now()
        response["Content-Disposition"] = f"attachment; filename=rekap_{now}.xlsx"

        wb.save(response)

        return response


def login_panitia_view(request):
    if request.method == "POST":
        wa = str(request.POST.get("wa")).strip()
        email = str(request.POST.get("email")).strip()
        juri = Juri.objects.filter(nomor_wa=wa, email=email).first()
        if not juri:
            messages.error(request, "Nomor WA atau kata sandi salah.")
            return redirect("sibijaks25:login_panitia")
        # Simpan informasi peserta di session
        user = authenticate(
            request, username="panitia", password=env("PASSWORD_PANITIA")
        )
        if user is not None:
            login(request, user)
            request.session["panitia"] = {
                "id": juri.id,
                "nama": juri.nama,
                "email": juri.email,
                "nomor_wa": juri.nomor_wa,
            }
            if not juri.is_panitia:
                # Redirect ke halaman naskah versi reviewer
                return redirect("sibijaks25:rev_naskah")
        else:
            messages.error(request, "Base user panitia belum dibuat.")
            return redirect("sibijaks25:login_panitia")
        # Redirect ke halaman naskah versi panitia
        return redirect("sibijaks25:panitia_naskah")
    return render(request, "sibijaks25/panitia/login.html")
