from django.contrib import admin
from .models import Artist, Artwork
from django.utils.html import format_html
from django.db import models

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
    fields = ('name', 'notes', 'profile_image', 'profile_image_preview')  # specify the order of fields
    readonly_fields = ('profile_image_preview',) 
    list_display = ('name', 'profile_image_preview')

    # def profile_image_preview(self, obj):
    #     return format_html('<img src="{}" height="50" />', obj.profile_image.url)
    # profile_image_preview.short_description = 'Profile Image'
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" height="70" />', obj.profile_image.url)
        else:
            return 'No Image'
    profile_image_preview.short_description = 'Profile Image'




admin.site.register(Artist, ArtistAdmin)
admin.site.register(Artwork)




# example of a custom admin site

# class ArtistAdminArea(admin.AdminSite):
#     site_header = 'Artist Admin area'
#     search_fields = ['name']

# art_db_site = ArtistAdminArea(name='Artists Admin')

# art_db_site.register(Artist, ArtistAdmin)
# art_db_site.register(Artwork)