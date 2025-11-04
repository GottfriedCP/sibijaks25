from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ...models import Peserta

import requests
import csv
import time

# CEK VARS DI BAWAH SEBELUM SEND
SUBYEK = "Undangan Coaching Clinic SiBijaKs Awards 2025"
TEMPLATE_PATH = "emails/m4.html"


class Command(BaseCommand):
    help = "Kirim email undangan coaching clinic."

    def add_arguments(self, parser):
        # parser.add_argument("poll_ids", nargs="+", type=int)
        # Named (optional) arguments
        parser.add_argument(
            "--real",
            action="store_true",
            help="Send the blast email for real.",
        )

    def handle(self, *args, **options):
        subyek = SUBYEK
        template_path = TEMPLATE_PATH

        pesertas_lolos = Peserta.objects.prefetch_related("naskahs")
        pesertas_lolos = pesertas_lolos.annotate(
            jml_naskah=Count("naskahs", filter=Q(naskahs__status_naskah=100))
        )
        pesertas_lolos = pesertas_lolos.filter(jml_naskah__gte=1)
        pesertas_lolos = pesertas_lolos.filter(
            Q(naskahs__naskah__isnull=True) | Q(naskahs__naskah="")
        )
        self.stdout.write(
            self.style.WARNING(
                f"{pesertas_lolos.count()} tim lolos ke tahap review full text dan belum unggah naskah FT."
            )
        )

        contacts = []
        for p in pesertas_lolos:
            contacts.append({"nama": p.nama, "email": p.email})
        # For testing, use a fixed contact list
        if not options["real"]:
            contacts = [
                {"nama": "Adi", "email": "gottfriedcpn@gmail.com"},
            ]

        emails = []
        with get_connection(fail_silently=True) as connection:
            for c in contacts:
                # Context yang disesuaikan untuk setiap penerima
                context = {
                    "nama": c["nama"],
                    "subyek": subyek,
                }

                # Render Template HTML
                html_message = render_to_string(template_path, context)
                plain_message = strip_tags(html_message)

                # Buat objek EmailMessage
                msg = EmailMultiAlternatives(
                    subject=subyek,
                    body=plain_message,
                    from_email="no-reply@kemkes.go.id",
                    to=[c["email"]],  # Hanya satu penerima per objek EmailMessage
                    connection=connection,  # Kaitkan objek pesan dengan koneksi yang sama
                    # reply_to=[],
                )
                msg.content_subtype = "html"  # Set konten sebagai HTML
                msg.attach_alternative(
                    html_message, "text/html"
                )  # Sisipkan konten HTML

                emails.append(msg)

            # 4. Kirim Semua Email dalam List
            # Fungsi .send_messages() mengirim semua objek EmailMessage melalui satu koneksi
            jumlah_terkirim = connection.send_messages(emails)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nFinished sending {jumlah_terkirim} emails to all contacts."
            )
        )
