from django.contrib import admin
from .models import Artist, Artwork
from django.utils.html import format_html
from django.db import models
from .arweave_storage import upload_to_arweave
import os

class ArtworkInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Artwork
    extra = 1  # number of extra forms to display
    readonly_fields = ('id','picture_preview', )
    fields = (
        'picture_preview', 
        'title', 
        'picture', 
        'picture_image_weaviate_id',
        'picture_url', 
        'year', 
        'sizeY', 
        'sizeX',
    )  # specify the order of fields

    def picture_preview(self, obj):
        if obj.picture_url:
            return format_html('<img src="{}" width="250" />', obj.picture_url)
        else:
            return 'No Image Found'
    picture_preview.short_description = 'Artwork Preview'

class ArtistAdmin(admin.ModelAdmin):
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
        'profile_image_url', 
        'profile_image_preview',
        'profile_image_weaviate_id',
        )  # specify the order of fields
    readonly_fields = ('id', 'profile_image_preview',) 
    list_display = ('full_name', 'id', 'profile_image_preview')

    def full_name(self, obj):
        if obj.firstname or obj.surname:
            return f"{obj.firstname or ''} {obj.surname or ''}"
        else:
            return "bez jmena"   

    def save_model(self, request, obj, form, change):

        # Handle saving profile image for the Artist
        if 'profile_image' in form.changed_data:
            obj.save()
            file_path = obj.profile_image.path
            arweave_url = upload_to_arweave(file_path)
            if arweave_url is not None:
                obj.profile_image_url = arweave_url
                # Delete the file from the media folder
                if os.path.isfile(file_path):
                    os.remove(file_path)

        super().save_model(request, obj, form, change)

    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # After the parent Artist model and related Artwork models are saved,
        # iterate over the Artwork instances and save their images in Arweave.
        for formset in formsets:
            for form in formset:
                if 'picture' in form.changed_data:
                    artwork = form.instance
                    artwork.save()
                    file_path = artwork.picture.path
                    arweave_url = upload_to_arweave(file_path)
                    if arweave_url is not None:
                        artwork.picture_url = arweave_url
                        artwork.save()
                        # Delete the file from the media folder
                        if os.path.isfile(file_path):
                            os.remove(file_path)
    

        


    def profile_image_preview(self, obj):
        if obj.profile_image_url:
            return format_html('<img src="{}" height="70" />', obj.profile_image_url)
        else:
            return 'No Image'
    profile_image_preview.short_description = 'Profile Image'


class ArtworkAdmin(admin.ModelAdmin):
    def title_to_display(self, obj):
        return obj.title or 'No title yet'
    list_display = ('title_to_display', 'id', 'artwork_image_preview')
    readonly_fields = ['artwork_image_preview_detail']

    def artwork_image_preview(self, obj):
        return format_html('<img src="{}" height="50" />', obj.picture_url)
    artwork_image_preview.short_description = 'Artwork Preview'

    def artwork_image_preview_detail(self, obj):
        return format_html('<img src="{}" width="350" />', obj.picture_url)
    artwork_image_preview_detail.short_description = 'Artwork Preview Detail'

    def save_model(self, request, obj, form, change):
        if 'picture' in form.changed_data:
            obj.save()
            file_path = obj.picture.path
            arweave_url = upload_to_arweave(file_path)
            if arweave_url is not None:
                obj.picture_url = arweave_url
                # Delete the file from the media folder
                if os.path.isfile(file_path):
                    os.remove(file_path)
        super().save_model(request, obj, form, change)



admin.site.register(Artist, ArtistAdmin)
admin.site.register(Artwork, ArtworkAdmin)
