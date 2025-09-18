from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import peserta_session_required, staff_required
from .forms import PesertaForm, NaskahForm, KolaboratorForm
from .models import Banner, Juri, Naskah, Peserta


@login_required
@staff_required
def naskah(request):
    """laman daftar naskah untuk panitia."""
    pesertas = Peserta.objects.all()
    jumlah_tim = pesertas.count()
    # hitung jumlah tim yang sudah submit minimal 1 naskah
    jumlah_tim_dengan_naskah = pesertas.filter(naskahs__isnull=False).count()
    naskahs = (
        Naskah.objects.select_related("peserta").prefetch_related("kolaborators").all()
    )
    context = {
        "jumlah_tim": jumlah_tim,
        "jumlah_tim_dengan_naskah": jumlah_tim_dengan_naskah,
        "jumlah_naskah": naskahs.count(),
        "jumlah_artikel": naskahs.filter(jenis_naskah=Naskah.ARTIKEL_ILMIAH).count(),
        "jumlah_pb": naskahs.filter(jenis_naskah=Naskah.POLICY_BRIEF).count(),
        "naskahs": naskahs,
    }
    return render(request, "sibijaks25/panitia/naskah.html", context)


@login_required
@staff_required
def detail_naskah(request, id):
    naskah = get_object_or_404(Naskah.objects.select_related("peserta"), id=id)
    ada_pasfoto = bool(getattr(naskah.peserta, "pasfoto", None))
    # TODO cek apa dia bisa assign juri untuk naskah ini (is_superuser atau is_panitia)
    context = {
        "naskah": naskah,
        "ada_pasfoto": ada_pasfoto,
    }
    return render(request, "sibijaks25/panitia/detail_naskah.html", context)


def login_panitia_view(request):
    if request.method == "POST":
        wa = request.POST.get("wa")
        email = request.POST.get("email")
        juri = Juri.objects.filter(nomor_wa=wa, email=email).first()
        if not juri:
            messages.error(request, "Nomor WA atau kata sandi salah.")
            return redirect("sibijaks25:login_panitia")
        # Simpan informasi peserta di session
        user = authenticate(request, username="user", password="user")
        if user is not None:
            login(request, user)
            request.session["panitia"] = {
                "id": juri.id,
                "nama": juri.nama,
                "email": juri.email,
                "nomor_wa": juri.nomor_wa,
            }
        else:
            messages.error(request, "Base user belum dibuat.")
            return redirect("sibijaks25:login_panitia")
        # Redirect ke halaman naskah versi panitia
        return redirect("sibijaks25:panitia_naskah")
    return render(request, "sibijaks25/panitia/login.html")
