from django.contrib import admin
from .models import Artist, Artwork
from django.utils.html import format_html
from django.db import models
from .arweave_storage import upload_to_arweave
import os

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
        'profile_image_preview'
        )  # specify the order of fields
    readonly_fields = ('profile_image_preview',) 
    list_display = ('full_name', 'profile_image_preview')

    def full_name(self, obj):
        if obj.firstname or obj.surname:
            return f"{obj.firstname or ''} {obj.surname or ''}"
        else:
            return "bez jmena"   

    def save_model(self, request, obj, form, change):
        if 'profile_image' in form.changed_data:
            obj.save()
            file_path = obj.profile_image.path
            arweave_url = upload_to_arweave(file_path)
            # obj.profile_image = None
            if arweave_url is not None:
                obj.profile_image_url = arweave_url
                # Delete the file from the media folder
                if os.path.isfile(file_path):
                    os.remove(file_path)
        super().save_model(request, obj, form, change)


    def profile_image_preview(self, obj):
        if obj.profile_image_url:
            return format_html('<img src="{}" height="70" />', obj.profile_image_url)
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
