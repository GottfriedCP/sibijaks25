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
    help = "Kirim pesan WA bagi peserta yang belum mengunggah naskah"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

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
        contacts = [
            {"nama": "Adi", "nomor_wa": "082213069594"},
        ]
        for c in contacts:
            nomor_wa = c["nomor_wa"]
            # Create a personalized message for each contact
            message = f"""
Yth. Ibu/Bapak {c['nama']}.

Kami ucapkan selamat atas naskah konsep policy brief/artikel imiah yang Ibu/Bapak kirimkan. Satu atau beberapa naskah telah dinyatakan *lolos seleksi* dan dapat dilanjutkan ke tahap berikutnya yaitu pengiriman naskah lengkap (full text). 

Langkah selanjutnya dapat kami sampaikan beberapa hal sebagai berikut:

1. Menindaklanjuti hasil penilaian dan mengunggah naskah full text pada website SiBijaKs Awards 2025.
2. Panduan penulisan policy brief dan artikel ilmiah mengacu pada instrumen penilaian naskah, dapat diakses pada link https://drive.google.com/drive/folders/1V2borxK4NEk6cFatfpuwm08bmpenhCRq?usp=sharing 
3. Kebutuhan data Survei Status Gizi Indonesia (SSGI) 2024 dapat diajukan melalui Portal Layanan Data Kementerian Kesehatan https://layanandata.kemkes.go.id/
4. Tata cara permintaan data dapat diakses di https://www.badankebijakan.kemkes.go.id/layanan-permintaan-data/ 
5. Batas waktu pengiriman naskah lengkap policy brief/artikel ilmiah pada *11 November 2025 pukul 23.59 WIB*
6. Silakan mengikuti workshop analisis data SSGI 2024 pada tanggal 15-16 Oktober 2025 pada link: https://s.kemkes.go.id/WorkshopAnalisisDataSSGI2024

Kami tunggu kiriman naskah lengkap policy brief/artikel ilmiah terbaiknya dengan menggunakan data SSGI 2024 sebagai sumber data utama.

Data SSGI 2024 Untuk Kebijakan Berkelanjutan
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
