from django.shortcuts import render
from .models import Banner


def index(request):
    banners = Banner.objects.filter(aktif=True).order_by("-date_created")
    context = {
        "banners": banners,
    }
    return render(request, "sibijaks25/index.html", context)
