from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import PesertaForm
from .models import Banner, Peserta


def index(request):
    banners = Banner.objects.filter(aktif=True).order_by("-date_created")
    context = {
        "banners": banners,
    }
    return render(request, "sibijaks25/index.html", context)


def registrasi(request):
    form = PesertaForm()
    if request.method == "POST":
        form = PesertaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registrasi peserta berhasil. Silakan login.")
            return redirect("sibijaks25:login")
        else:
            messages.error(request, "Terjadi kesalahan pengisian form.")
    context = {
        "form": form,
    }
    return render(request, "sibijaks25/registrasi.html", context)


@login_required
def naskah(request):
    return render(request, "sibijaks25/naskah.html")


@login_required
def tambah_naskah(request):
    pass


@login_required
def kolaborator(request):
    pass


@login_required
def tambah_kolaborator(request):
    pass


def login_view(request):
    if request.method == "POST":
        wa = request.POST.get("wa")
        email = request.POST.get("email")
        peserta = Peserta.objects.filter(nomor_wa=wa, email=email).first()
        if not peserta:
            messages.error(request, "Nomor WA atau kata sandi salah.")
            return redirect("sibijaks25:login")
        # Simpan informasi peserta di session
        user = authenticate(request, username="user", password="user")
        if user is not None:
            login(request, user)
            request.session["peserta"] = {
                "id": peserta.id,
                "nama": peserta.nama,
                "email": peserta.email,
                "nomor_wa": peserta.nomor_wa,
            }
        else:
            messages.error(request, "Base user belum dibuat.")
            return redirect("sibijaks25:login")
        # Redirect ke halaman naskah
        return redirect("sibijaks25:naskah")
    return render(request, "sibijaks25/login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("sibijaks25:index")
