from django import forms
from .models import Peserta, Juri, Naskah, Kolaborator


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


class FotoPesertaForm(forms.ModelForm):
    class Meta:
        model = Peserta
        fields = ["pasfoto"]


class NaskahForm(forms.ModelForm):
    class Meta:
        model = Naskah
        fields = ["judul", "jenis_naskah", "abstrak", "file_abstrak", "kolaborators"]

    def __init__(self, *args, peserta=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kolaborators"].widget = forms.CheckboxSelectMultiple()
        if peserta is not None:
            self.fields["kolaborators"].queryset = Kolaborator.objects.filter(
                peserta=peserta
            )


class NaskahFTForm(forms.ModelForm):
    class Meta:
        model = Naskah
        fields = [
            "judul",
            "naskah",
            "kolaborators",
        ]

    def __init__(self, *args, peserta=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kolaborators"].widget = forms.CheckboxSelectMultiple()
        if peserta is not None:
            self.fields["kolaborators"].queryset = Kolaborator.objects.filter(
                peserta=peserta
            )


class NaskahKolaboratorForm(forms.ModelForm):
    class Meta:
        model = Naskah
        fields = ["kolaborators"]

    def __init__(self, *args, peserta=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kolaborators"].widget = forms.CheckboxSelectMultiple()
        if peserta is not None:
            self.fields["kolaborators"].queryset = Kolaborator.objects.filter(
                peserta=peserta
            )


class NaskahJuriForm(forms.ModelForm):
    class Meta:
        model = Naskah
        fields = ["juris"]

    def __init__(self, *args, rev_only=None, **kwargs):
        super().__init__(*args, **kwargs)
        if rev_only:
            self.fields["juris"].queryset = Juri.objects.filter(is_panitia=False)


class KolaboratorForm(forms.ModelForm):
    class Meta:
        model = Kolaborator
        fields = ["nama", "nomor_wa", "email", "institusi", "pekerjaan", "pendidikan"]
