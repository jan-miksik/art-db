from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
# from artists import views

urlpatterns = [
    # path('admin-art-db/', art_db_site.urls),
    path('', admin.site.urls),
    # path('', views.artist_list, name='artist_list'),
    # path('admin/', admin.site.urls),
    path('artists/', include('artists.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.index_title = 'Art DB'
admin.site.site_header = 'Art DB Admin' 
admin.site.site_title = 'Art DB Admin'