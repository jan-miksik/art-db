from django.urls import path
from .views import artists_endpoint
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', artists_endpoint),
    path('upload-to-arweave/<int:pk>/', csrf_exempt(views.upload_to_arweave_view), name='upload_to_arweave'),
    path('search-artworks-by-image-url/', csrf_exempt(views.search_artworks_by_image_url), name='search_artworks_by_image_url'),
    path('search-artworks-by-image-data/', csrf_exempt(views.search_artworks_by_image_data), name='search_artworks_by_image_data'),
    path('search-authors-by-image-data/', csrf_exempt(views.search_authors_by_image_data), name='search_authors_by_image_data'),
    path('search-authors-by-image-url/', csrf_exempt(views.search_authors_by_image_url), name='search_authors_by_image_url'),

]
