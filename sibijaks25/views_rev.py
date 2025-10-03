from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import peserta_session_required, staff_required
from .forms import NaskahJuriForm
from .models import Banner, Juri, Naskah, Peserta, Review1, Review2

from environs import env

env.read_env()


@login_required
@staff_required
def naskah(request):
    """laman daftar naskah untuk panitia."""
    juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
    revs = Review2.objects.filter(juri=juri).select_related("naskah")
    naskahs_list = []
    for r in revs:
        bisa_dinilai = r.total < 1
        naskahs_list.append((r.naskah, bisa_dinilai))
    context = {
        "juri": juri,
        "naskahs": naskahs_list,
    }
    return render(request, "sibijaks25/rev/naskah.html", context)


@login_required
@staff_required
def detail_naskah(request, id):
    juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
    naskah = get_object_or_404(Naskah.objects.select_related("peserta"), id=id)
    jenis_naskah = "ai" if naskah.jenis_naskah == naskah.ARTIKEL_ILMIAH else "pb"
    
    context = {
        "naskah": naskah,
        "juri": juri,
        "jenis_naskah": jenis_naskah,
    }
    return render(request, "sibijaks25/rev/detail_naskah.html", context)


@login_required
@staff_required
def simpan_penilaian(request):
    if request.method == "POST":
        juri = get_object_or_404(Juri, id=request.session["panitia"]["id"])
        id_naskah = request.POST.get("id_naskah")
        naskah = get_object_or_404(Naskah, id=id_naskah)
        # form data
        rev = get_object_or_404(Review2, juri=juri, naskah=naskah)
        messages.success(request, "Penilaian berhasil disimpan.")
        return redirect("sibijaks25:rev_naskah")
    return redirect("sibijaks25:rev_detail_naskah", id=naskah.id)
