from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PesertaForm, NaskahForm, KolaboratorForm
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
            peserta = form.save()
            if peserta.is_mahasiswa:
                peserta.pekerjaan = (
                    f"Mahasiswa {Peserta.MAHASISWA_CHOICES.get(peserta.mahasiswa)}"
                )
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
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.prefetch_related("kolaborators", "naskahs").get(
        nomor_wa=wa, email=email
    )
    jumlah_kolaborator = peserta.kolaborators.count()
    ada_kolaborator = jumlah_kolaborator > 0
    if not ada_kolaborator:
        messages.warning(
            request,
            "Anda belum menambahkan kolaborator. Silakan tambahkan kolaborator terlebih dahulu (minimal 1 orang).",
        )
    naskahs = peserta.naskahs.all()
    context = {
        "ada_kolaborator": ada_kolaborator,
        "kolaborators": peserta.kolaborators.all(),
        "naskahs": naskahs,
    }
    return render(request, "sibijaks25/naskah.html", context)


@login_required
def edit_naskah(request, id):
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.get(nomor_wa=wa, email=email)
    naskah = peserta.naskahs.filter(id=id).first()
    if not naskah:
        messages.error(request, "Naskah tidak ditemukan.")
        return redirect("sibijaks25:naskah")
    form = NaskahForm(instance=naskah, peserta=peserta)
    if request.method == "POST":
        form = NaskahForm(request.POST, request.FILES, instance=naskah, peserta=peserta)
        if form.is_valid():
            form.save()
            messages.success(request, "Naskah berhasil diperbarui.")
            return redirect("sibijaks25:naskah")
        else:
            messages.error(request, "Terjadi kesalahan pengisian form.")
    context = {
        "form": form,
        "naskah": naskah,
    }
    return render(request, "sibijaks25/edit_naskah.html", context)


@login_required
def tambah_naskah(request):
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.get(nomor_wa=wa, email=email)
    form = NaskahForm(peserta=peserta)
    if request.method == "POST":
        form = NaskahForm(request.POST, request.FILES, peserta=peserta)
        if form.is_valid():
            naskah = form.save(commit=False)
            naskah.peserta = peserta
            naskah.save()
            form.save_m2m()
            messages.success(request, "Naskah berhasil didaftarkan.")
            return redirect("sibijaks25:naskah")
        else:
            messages.error(request, "Terjadi kesalahan pengisian form.")
    context = {
        "form": form,
    }
    return render(request, "sibijaks25/tambah_naskah.html", context)


@login_required
def hapus_naskah(request, id):
    if request.method == "POST":
        wa = request.session.get("peserta", {}).get("nomor_wa")
        email = request.session.get("peserta", {}).get("email")
        peserta = Peserta.objects.get(nomor_wa=wa, email=email)
        naskah = peserta.naskahs.filter(id=id).first()
        if not naskah:
            messages.error(request, "Naskah tidak ditemukan.")
            return redirect("sibijaks25:naskah")
        naskah.delete()
        messages.success(request, "Naskah berhasil dihapus.")

    return redirect("sibijaks25:naskah")


@login_required
def detail_naskah(request, id):
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.get(nomor_wa=wa, email=email)
    naskah = peserta.naskahs.filter(id=id).first()
    context = {
        "naskah": naskah,
    }
    return render(request, "sibijaks25/detail_naskah.html", context)


@login_required
def kolaborator(request):
    pass


@login_required
def edit_kolaborator(request, id):
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.get(nomor_wa=wa, email=email)
    kolaborator = peserta.kolaborators.filter(id=id).first()
    if not kolaborator:
        messages.error(request, "Kolaborator tidak ditemukan.")
        return redirect("sibijaks25:naskah")
    form = KolaboratorForm(instance=kolaborator)
    if request.method == "POST":
        form = KolaboratorForm(request.POST, request.FILES, instance=kolaborator)
        if form.is_valid():
            form.save()
            messages.success(request, "Kolaborator berhasil diperbarui.")
            return redirect("sibijaks25:naskah")
        else:
            messages.error(request, "Terjadi kesalahan pengisian form.")
    context = {
        "form": form,
        "kolaborator": kolaborator,
    }
    return render(request, "sibijaks25/edit_kolaborator.html", context)


@login_required
def tambah_kolaborator(request):
    form = KolaboratorForm()
    if request.method == "POST":
        form = KolaboratorForm(request.POST)
        if form.is_valid():
            wa = request.session.get("peserta", {}).get("nomor_wa")
            email = request.session.get("peserta", {}).get("email")
            peserta = Peserta.objects.get(nomor_wa=wa, email=email)
            kolaborator = form.save(commit=False)
            kolaborator.peserta = peserta
            kolaborator.save()
            messages.success(request, "Kolaborator berhasil ditambahkan.")
            return redirect("sibijaks25:naskah")
        else:
            messages.error(request, "Terjadi kesalahan pengisian form.")

    context = {
        "form": form,
    }
    return render(request, "sibijaks25/tambah_kolaborator.html", context)


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
