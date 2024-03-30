from django import forms
from .models import Artist

class ArtistAdminForm(forms.ModelForm):
    file_upload = forms.FileField(required=False, label='Upload File to Arweave')

    class Meta:
        model = Artist
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        file_upload = self.cleaned_data.get('file_upload')
        if file_upload:
            from artists.arweave_storage import upload_to_arweave
            file_path = file_upload.temporary_file_path()
            arweave_url = upload_to_arweave(file_path)
            instance.profile_image_url = arweave_url
        if commit:
            instance.save()
        return instance