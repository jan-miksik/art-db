# Create your views here.
from django.shortcuts import render, redirect
from .models import Artist
from rest_framework import viewsets
from .serializers import ArtistSerializer, ArtworkSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from artists.arweave_storage import upload_to_arweave
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Artist
from django.views.decorators.csrf import csrf_protect
from .weaviate.weaviate import search_similar_artwork_ids_by_image_url, search_similar_artwork_ids_by_image_data
from .models import Artwork, Artist
import base64

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
def search_artworks_by_image_url(request):
    image_url = request.GET.get('image_url')
    limit = int(request.GET.get('limit', 1))
    similar_images = search_similar_artwork_ids_by_image_url(image_url, limit)

    # Get the corresponding Artwork and Artist objects
    response_data = []
    for image in similar_images:
        artwork = Artwork.objects.filter(id=image.properties['artwork_psql_id']).first()
        author = Artist.objects.filter(id=image.properties['author_psql_id']).first()

        if artwork and author:
            # Serialize the Artwork and Artist objects
            artwork_serializer = ArtworkSerializer(artwork)
            author_serializer = ArtistSerializer(author)
            response_data.append({
                'artwork': artwork_serializer.data,
                'author': author_serializer.data,
            })

    return Response(response_data)

# http://localhost:8000/artists/search-artworks-by-image-url/?image_url=https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU&limit=1


@api_view(['POST'])
def search_artworks_by_image_data(request):
    image_file = request.FILES.get('image')
    limit = int(request.data.get('limit', 2))

    if image_file:
        # Read the file data into bytes
        image_data_bytes = image_file.read()

        # Convert bytes to base64 string (optional)
        # image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')

        similar_images = search_similar_artwork_ids_by_image_data(image_data_bytes, limit)
        response_data = []
        for image in similar_images:
            artwork = Artwork.objects.filter(id=image.properties['artwork_psql_id']).first()
            author = Artist.objects.filter(id=image.properties['author_psql_id']).first()
            if artwork and author:
                artwork_serializer = ArtworkSerializer(artwork)
                author_serializer = ArtistSerializer(author)
                response_data.append({
                    'artwork': artwork_serializer.data,
                    'author': author_serializer.data,
                })
        return Response(response_data)
    else:
        return Response({'error': 'Image data not provided'}, status=400)
    
@api_view(['POST'])
def search_authors_by_image_data(request):
    image_file = request.FILES.get('image')
    limit = int(request.data.get('limit', 2))

    if image_file:
        # Read the file data into bytes
        image_data_bytes = image_file.read()

        # Convert bytes to base64 string (optional)
        # image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')

        similar_images = search_similar_artwork_ids_by_image_data(image_data_bytes, limit)
        response_data = []
        for image in similar_images:
            artwork = Artwork.objects.filter(id=image.properties['artwork_psql_id']).first()
            author = Artist.objects.filter(id=image.properties['author_psql_id']).first()
            if artwork and author:
                artwork_serializer = ArtworkSerializer(artwork)
                author_serializer = ArtistSerializer(author)
                response_data.append({
                    'artwork': artwork_serializer.data,
                    'author': author_serializer.data,
                })
        return Response(response_data)
    else:
        return Response({'error': 'Image data not provided'}, status=400)