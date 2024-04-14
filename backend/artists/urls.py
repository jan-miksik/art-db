from django.urls import include, path
# from . import views
# from rest_framework.routers import DefaultRouter
from .views import artists_endpoint
from . import views
from django.views.decorators.csrf import csrf_exempt

# from .views import ArtistViewSet
# router = DefaultRouter()
# router.register(r'artists', ArtistViewSet)

urlpatterns = [
    path('', artists_endpoint),
    path('upload-to-arweave/<int:pk>/', csrf_exempt(views.upload_to_arweave_view), name='upload_to_arweave'),
    path('search-authors-by-image/', views.search_authors_by_image_view, name='search_authors_by_image'),

    # path('', views.artist_list, name='artist_list'),
    # path('create/', views.artist_create, name='artist_create'),
    # path('artists_registry/', include('artists_registry.urls')),
]