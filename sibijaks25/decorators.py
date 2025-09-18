from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def peserta_session_required(view_func):
    """Decorator to check if 'peserta' session data exists."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        peserta = request.session.get("peserta")
        if not peserta or not peserta.get("nomor_wa") or not peserta.get("email"):
            messages.error(request, "Silakan login sebagai peserta.")
            return redirect("sibijaks25:login")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url="sibijaks25:login")(
        view_func
    )
