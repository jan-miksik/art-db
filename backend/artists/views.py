# Create your views here.
from django.shortcuts import render, redirect
from .models import Artist
from rest_framework import viewsets
from .serializers import ArtistSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from artists.arweave_storage import upload_to_arweave
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Artist
from django.views.decorators.csrf import csrf_protect
from .weaviate.weaviate import search_similar_images_by_image_url

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


@api_view(['GET'])
def artists_endpoint(request):
    models = Artist.objects.all()
    serializer = ArtistSerializer(models, many=True)
    return Response(serializer.data)



@csrf_protect
def upload_to_arweave_view(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            file_path = file.temporary_file_path()
            arweave_url = upload_to_arweave(file_path)
            return JsonResponse({'success': True, 'url': arweave_url})
        return JsonResponse({'success': False, 'error': 'No file provided'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@api_view(['GET'])
def search_authors_by_image_view(request):
    image_url = request.GET.get('image_url')
    limit = int(request.GET.get('limit', 2))
    similar_images = search_similar_images_by_image_url(image_url, limit)
    # TODO return unique authors of images from search_similar_images_by_image_url ?
    # TODO return authors of images, call to db for artist with psql_id

    return Response(similar_images)