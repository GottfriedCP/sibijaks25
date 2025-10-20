from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from ...models import Peserta

import requests
import csv
import time

# The API endpoint URL
url = "https://app.whacenter.com/api/send"
DEVICE_ID = "7b7bb304e8173a8feb020ac49a707be2"


class Command(BaseCommand):
    help = "Kirim pesan WA how-tp permintaan data SSGI"

    def add_arguments(self, parser):
        # parser.add_argument("poll_ids", nargs="+", type=int)
        # Named (optional) arguments
        parser.add_argument(
            "--real",
            action="store_true",
            help="Send the blast message for real.",
        )

    def handle(self, *args, **options):
        pesertas_lolos = Peserta.objects.annotate(
            jml_naskah=Count("naskahs", filter=Q(naskahs__status_naskah=100))
        ).filter(jml_naskah__gte=1)
        self.stdout.write(
            self.style.WARNING(
                f"{pesertas_lolos.count()} tim lolos tahap review konsep."
            )
        )
        # return
        contacts = []
        for p in pesertas_lolos:
            contacts.append({"nama": p.nama, "nomor_wa": p.nomor_wa})
        # For testing, use a fixed contact list
        if not options["real"]:
            contacts = [
                {"nama": "Adi", "nomor_wa": "082213069594"},
            ]
        for c in contacts:
            nomor_wa = c["nomor_wa"]
            # Create a personalized message for each contact
            message = f"""
Yth. Peserta SiBijaKs Awards 2025,

Terkait dengan permintaan data, Bapak/Ibu dapat mengajukan ke portal layanan data https://layanandata.kemkes.go.id dengan mengunggah surat permohonan berikut https://drive.google.com/file/d/1EdmLBMwHyizBgIpTCXL-BQCOY2E0o4jY/view?usp=sharing untuk kelengkapan permohonan data, serta melampirkan kode variabel yang dibutuhkan seperti tercantum pada tautan https://layanandata.kemkes.go.id/katalog-data 

*Permintaan data dan unggah NDA paling lambat diterima oleh portal layanan data pada hari Rabu, 22 Oktober 2025 pukul 23:59 WIB.* 

Permohonan data akan diterima oleh peserta paling lambat pada hari Jumat, 31 Oktober 2025 pukul 23:59 WIB.

Mohon cek status permintaan data secara berkala melalui portal layanan data.

Jika masih ada yang ingin ditanyakan, bisa melalui email ke: sibijaksawards2025@gmail.com a.n. Dian Widiati.

---
Terima kasih dan Salam sehat,
Panitia SiBijaKs Awards 2025"""

            # Prepare the data payload for the API request
            payload = {
                "device_id": DEVICE_ID,
                "number": nomor_wa,
                "message": message,
            }

            try:
                self.stdout.write(f"Sending message to: {c['nama']} ({nomor_wa})...")
                # Send the POST request
                response = requests.post(url, data=payload)
                # Raise an exception for bad HTTP status codes (4xx or 5xx)
                response.raise_for_status()

                # Print the server's response
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  -> Request successful. Response: {response.text.strip()}"
                    )
                )

            except requests.exceptions.RequestException as e:
                # Handle potential network errors or bad responses
                self.stdout.write(
                    self.style.ERROR(
                        f"  -> An error occurred while sending to {c['nama']}: {e}"
                    )
                )

            # Add a small delay between requests to avoid overwhelming the API
            time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS("\nFinished sending messages to all contacts.")
        )
