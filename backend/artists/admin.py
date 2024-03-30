from django.contrib import admin
from .models import Artist, Artwork
from django.utils.html import format_html
from django.db import models
from django import forms

# from artists.arweave_storage import upload_to_arweave
# from django.shortcuts import render
# from django.http import HttpResponseRedirect
# from artists.forms import ArtistAdminForm

from .arweave_storage import upload_to_arweave







class ArtistAdminForm(forms.ModelForm):
    file_upload = forms.FileField(required=False, label='Upload File to Arweave')

    class Meta:
        model = Artist
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        file_upload = self.cleaned_data.get('file_upload')
        if file_upload:
            file_path = file_upload.temporary_file_path()
            arweave_url = upload_to_arweave(file_path)
            instance.profile_image_url = arweave_url
        if commit:
            instance.save()
        return instance






class ArtworkInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Artwork
    extra = 1  # number of extra forms to display
    picture = models.ImageField(upload_to='artworks/')
    readonly_fields = ('picture_preview', )

    def picture_preview(self,obj):
        if self.picture:
            return format_html('<img src="{}" width="250" />', obj.picture.url)
        else:
            return 'No Image Found'
    picture_preview.short_description = 'Artwork Preview'

# @admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # form = ArtistForm
    form = ArtistAdminForm
    site_header = 'Artist Admin area'
    inlines = [ArtworkInline]
    fields = (
        'firstname', 
        'surname',
        'born',
        'gender',
        'auctions_turnover_2023_h1_USD',
        'notes', 
        'profile_image',
        'file_field',
        'profile_image_url', 
        'profile_image_preview'
        )  # specify the order of fields
    readonly_fields = ('profile_image_preview',) 
    list_display = ('full_name', 'profile_image_preview')

    # def upload_to_arweave_action(self, request, queryset):
    #     if 'apply' in request.POST:
    #         file = request.FILES.get('file')
    #         if file:
    #             file_path = file.temporary_file_path()
    #             arweave_url = upload_to_arweave(file_path)
    #             selected_artists = queryset.values_list('id', flat=True)
    #             Artist.objects.filter(id__in=selected_artists).update(profile_image_url=arweave_url)
    #             self.message_user(request, f"File uploaded successfully. Arweave URL: {arweave_url}")
    #             return HttpResponseRedirect(request.get_full_path())
    #     return render(request, 'admin/upload_to_arweave.html', context={'artists': queryset})

    # upload_to_arweave_action.short_description = "Upload file to Arweave"
    # actions = ['upload_to_arweave_action']

    def full_name(self, obj):
        if obj.firstname or obj.surname:
            return f"{obj.firstname or ''} {obj.surname or ''}"
        else:
            return "bez jmena"

    # def profile_image_preview(self, obj):
    #     return format_html('<img src="{}" height="50" />', obj.profile_image.url)
    # profile_image_preview.short_description = 'Profile Image'
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" height="70" />', obj.profile_image.url)
        else:
            return 'No Image'
    profile_image_preview.short_description = 'Profile Image'





class ArtworkAdmin(admin.ModelAdmin):
    def title_to_display(self, obj):
        return obj.title or 'No title yet'
    list_display = ('title_to_display', 'artwork_image_preview')

    readonly_fields = ['artwork_image_preview_detail']

    def artwork_image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.picture.url)
    artwork_image_preview.short_description = 'Artwork Preview'

    def artwork_image_preview_detail(self, obj):
        return format_html('<img src="{}" width="350" />', obj.picture.url)
    artwork_image_preview.short_description = 'Artwork Preview'



admin.site.register(Artist, ArtistAdmin)
admin.site.register(Artwork, ArtworkAdmin)





# example of a custom admin site

# class ArtistAdminArea(admin.AdminSite):
#     site_header = 'Artist Admin area'
#     search_fields = ['name']

# art_db_site = ArtistAdminArea(name='Artists Admin')

# art_db_site.register(Artist, ArtistAdmin)
# art_db_site.register(Artwork)