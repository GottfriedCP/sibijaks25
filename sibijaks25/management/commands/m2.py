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
SUBYEK = "SiBijaKs Awards 2025 - Undangan Mengikuti Health Policy Conference"
TEMPLATE_PATH = "emails/m10.html"
# FILEPATH = settings.BASE_DIR / "static" / "file" / "Pemberitahuan_Pelaksanaan_Konferensi.pdf"
FILEPATH = False
MIMETYPE = "application/pdf"


class Command(BaseCommand):
    help = "Kirim email"

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

        # Ambil data peserta
        pesertas_lolos = Peserta.objects.annotate(jml_naskah=Count("naskahs")).filter(
            jml_naskah__gte=1
        )
        self.stdout.write(
            self.style.WARNING(
                f"{pesertas_lolos.count()} email(s) to send."
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
                    reply_to=["no-reply@kemkes.go.id"],
                )
                msg.content_subtype = "html"  # Set konten sebagai HTML
                msg.attach_alternative(
                    html_message, "text/html"
                )  # Sisipkan konten HTML
                if FILEPATH:
                    msg.attach_file(FILEPATH, MIMETYPE)

                emails.append(msg)

            # 4. Kirim Semua Email dalam List
            # Fungsi .send_messages() mengirim semua objek EmailMessage melalui satu koneksi
            jumlah_terkirim = connection.send_messages(emails)

        self.stdout.write(
            self.style.SUCCESS(f"\nFinished sending {jumlah_terkirim} emails.")
        )
