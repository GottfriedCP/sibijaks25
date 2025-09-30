from django.utils import timezone
from django.http import Http404


def _cek_deadline():
    over_date = timezone.make_aware(timezone.datetime(2025, 10, 1, 0, 0, 0))
    if timezone.now() >= over_date:
        raise Http404("Kedaluwarsa")
