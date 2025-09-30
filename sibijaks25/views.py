from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import peserta_session_required
from .forms import FotoPesertaForm, PesertaForm, NaskahForm, KolaboratorForm
from .helpers import _cek_deadline
from .models import Banner, Countdown, Naskah, Peserta


def index(request):
    banners = Banner.objects.filter(aktif=True).order_by("-date_created")
    countdowns = Countdown.objects.filter(aktif=True).order_by("-date_created")
    pesertas = Peserta.objects.all()
    jumlah_tim = pesertas.count()
    # hitung jumlah tim yang sudah submit minimal 1 naskah
    jumlah_tim_dengan_naskah = pesertas.filter(naskahs__isnull=False).distinct().count()
    naskahs = (
        Naskah.objects.select_related("peserta").prefetch_related("kolaborators").all()
    )
    context = {
        "banners": banners,
        "countdowns": countdowns,
        "jumlah_tim": jumlah_tim,
        "jumlah_tim_dengan_naskah": jumlah_tim_dengan_naskah,
        "jumlah_naskah": naskahs.count(),
        "jumlah_artikel": naskahs.filter(jenis_naskah=Naskah.ARTIKEL_ILMIAH).count(),
        "jumlah_pb": naskahs.filter(jenis_naskah=Naskah.POLICY_BRIEF).count(),
    }
    return render(request, "sibijaks25/index.html", context)


def registrasi(request):
    _cek_deadline()
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
@peserta_session_required
def unggah_foto(request, peserta_id):
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.prefetch_related("kolaborators", "naskahs").get(
        nomor_wa=wa, email=email
    )
    form = FotoPesertaForm(instance=peserta)
    if request.method == "POST":
        form = FotoPesertaForm(request.POST, request.FILES, instance=peserta)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto berhasil diunggah.")
            return redirect("sibijaks25:naskah")
        else:
            messages.error(request, "Terjadi kesalahan pengisian form.")
    context = {
        "form": form,
        "peserta": peserta,
    }
    return render(request, "sibijaks25/unggah_foto.html", context)


@login_required
@peserta_session_required
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
    ada_pasfoto = bool(getattr(peserta, "pasfoto", None))
    context = {
        "peserta": peserta,
        "ada_kolaborator": ada_kolaborator,
        "kolaborators": peserta.kolaborators.all(),
        "naskahs": naskahs,
        "ada_pasfoto": ada_pasfoto,
    }
    return render(request, "sibijaks25/naskah.html", context)


@login_required
@peserta_session_required
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
@peserta_session_required
def tambah_naskah(request):
    _cek_deadline()
    wa = request.session.get("peserta", {}).get("nomor_wa")
    email = request.session.get("peserta", {}).get("email")
    peserta = Peserta.objects.get(nomor_wa=wa, email=email)
    # cek apa ada minimal 1 kolaborator dan pasfoto
    if peserta.kolaborators.count() < 1:
        messages.error(
            request,
            "Anda harus menambahkan minimal 1 kolaborator sebelum menambahkan naskah.",
        )
        return redirect("sibijaks25:naskah")
    if not bool(getattr(peserta, "pasfoto", None)):
        messages.error(
            request,
            "Anda harus mengunggah pasfoto sebelum menambahkan naskah.",
        )
        return redirect("sibijaks25:naskah")
    
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
@peserta_session_required
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
@peserta_session_required
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
@peserta_session_required
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
        wa = str(request.POST.get("wa")).strip()
        email = str(request.POST.get("email")).strip()
        peserta = Peserta.objects.filter(nomor_wa=wa, email=email).first()
        if not peserta:
            messages.error(request, "Nomor WA atau email salah.")
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
