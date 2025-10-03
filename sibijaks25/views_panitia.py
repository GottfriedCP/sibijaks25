from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import peserta_session_required, staff_required
from .forms import NaskahJuriForm
from .models import Banner, Juri, Naskah, Peserta, Review1

from environs import env

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
        naskahs_list.append((n, bisa_dinilai, jumlah_juri))
    context = {
        "juri": juri,
        "jumlah_tim": jumlah_tim,
        "jumlah_tim_dengan_naskah": jumlah_tim_dengan_naskah,
        "jumlah_naskah": naskahs.count(),
        "jumlah_artikel": naskahs.filter(jenis_naskah=Naskah.ARTIKEL_ILMIAH).count(),
        "jumlah_pb": naskahs.filter(jenis_naskah=Naskah.POLICY_BRIEF).count(),
        "naskahs": naskahs_list,
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
        if not juri.is_supersubstansi:
            messages.error(request, "Hanya super substansi yang bisa mengubah juri.")
            return redirect("sibijaks25:panitia_naskah")
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
        jml_naskah = r.naskahs.count()
        reviewers_list.append((r, jml_naskah))
    context = {
        "naskah": naskah,
        "juri": juri,
        "ada_pasfoto": ada_pasfoto,
        "bisa_dinilai": bisa_dinilai,
        "is_supersubstansi": juri.is_supersubstansi,
        "form_juri": (
            NaskahJuriForm(instance=naskah) if juri.is_supersubstansi else None
        ),
        "reviewers": reviewers_list,
    }
    return render(request, "sibijaks25/panitia/detail_naskah.html", context)


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
