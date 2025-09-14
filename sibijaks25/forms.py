from django import forms
from .models import Peserta, Naskah, Kolaborator


class PesertaForm(forms.ModelForm):
    class Meta:
        model = Peserta
        fields = [
            "nama",
            "email",
            "nomor_wa",
            "is_mahasiswa",
            "mahasiswa",
            "institusi",
            "pekerjaan",
            "pendidikan",
            "pasfoto",
        ]


class NaskahForm(forms.ModelForm):
    class Meta:
        model = Naskah
        fields = ["judul", "jenis_naskah", "abstrak", "kolaborators"]

    def __init__(self, *args, peserta=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kolaborators"].widget = forms.CheckboxSelectMultiple()
        if peserta is not None:
            self.fields["kolaborators"].queryset = Kolaborator.objects.filter(
                peserta=peserta
            )


class KolaboratorForm(forms.ModelForm):
    class Meta:
        model = Kolaborator
        fields = ["nama", "nomor_wa", "email", "institusi"]
