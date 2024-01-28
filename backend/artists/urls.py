from django.urls import include, path
# from . import views
# from rest_framework.routers import DefaultRouter
from .views import artists_endpoint

# from .views import ArtistViewSet
# router = DefaultRouter()
# router.register(r'artists', ArtistViewSet)

urlpatterns = [
    path('', artists_endpoint),
    # path('', views.artist_list, name='artist_list'),
    # path('create/', views.artist_create, name='artist_create'),
    # path('artists_registry/', include('artists_registry.urls')),
]