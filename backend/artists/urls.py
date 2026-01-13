from django.urls import path
from .views import artists_endpoint
from . import views

# NOTE: CSRF exemptions removed for security.
# For API authentication, consider implementing one of:
# 1. DRF Token Authentication (SessionAuthentication handles CSRF automatically)
# 2. JWT tokens with django-rest-framework-simplejwt
# 3. API keys for machine-to-machine communication
#
# For now, ensure your frontend sends CSRF tokens with requests:
# - Include csrftoken cookie in requests
# - Or use SessionAuthentication which handles CSRF via cookies

urlpatterns = [
    path('', artists_endpoint),
    path('upload-to-arweave/<int:pk>/', views.upload_to_arweave_view, name='upload_to_arweave'),
    path('search-artworks-by-image-url/', views.search_artworks_by_image_url, name='search_artworks_by_image_url'),
    path('search-artworks-by-image-data/', views.search_artworks_by_image_data, name='search_artworks_by_image_data'),
    path('search-authors-by-image-data/', views.search_authors_by_image_data, name='search_authors_by_image_data'),
    path('search-authors-by-image-url/', views.search_authors_by_image_url, name='search_authors_by_image_url'),
]
