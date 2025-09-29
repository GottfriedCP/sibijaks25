from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from ...models import Peserta

import requests
import csv
import time

# The API endpoint URL
url = "https://app.whacenter.com/api/send"
DEVICE_ID = "7b7bb304e8173a8feb020ac49a707be2"


class Command(BaseCommand):
    help = "Kirim pesan WA bagi peserta yang belum mengunggah naskah"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        pesertas_belum_unggah = Peserta.objects.annotate(jml_naskah=Count("naskahs"))
        pesertas_belum_unggah = pesertas_belum_unggah.filter(jml_naskah=0)
        if not pesertas_belum_unggah.exists():
            self.stdout.write(
                self.style.SUCCESS("Semua peserta sudah mengunggah naskah.")
            )
            return
        self.stdout.write(
            self.style.WARNING(
                f"{pesertas_belum_unggah.count()} peserta belum mengunggah naskah."
            )
        )
        # return
        contacts = []
        for p in pesertas_belum_unggah:
            contacts.append({"nama": p.nama, "nomor_wa": p.nomor_wa})
        # For testing, use a fixed contact list
        # contacts = [
        #     {"nama": "Adi", "nomor_wa": "082213069594"},
        # ]
        for c in contacts:
            nomor_wa = c["nomor_wa"]
            # Create a personalized message for each contact
            message = f"""
*1 Hari Lagi Batas Waktu Unggah Naskah SiBijaKs Awards 2025*

Selamat siang, Ibu/Bapak {c['nama']}.

Terima kasih sudah mendaftar untuk berpartisipasi dalam ajang SiBijaKs Awards 2025.
Tidak terasa batas akhir pengumpulan konsep naskah SiBijaks Awards 2025 tinggal 1 hari lagi.
Yuk, segera unggah konsep naskah terbaiknya sebelum tanggal 30 September 2025 pukul 23:59 WIB.

*Data SSGI 2024 Untuk Kebijakan Berkelanjutan*
---
Salam sehat,
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
