import os
from tempfile import NamedTemporaryFile

from rest_framework import viewsets
from .serializers import ArtistSerializer, ArtworkSerializer, SearchArtistSerializer
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from artists.arweave_storage import upload_to_arweave
from django.shortcuts import get_object_or_404
from .weaviate.weaviate import search_similar_artwork_ids_by_image_url, search_similar_artwork_ids_by_image_data, \
    search_similar_authors_ids_by_image_data, search_similar_authors_ids_by_image_url
from .models import Artwork, Artist
from .throttles import SearchAnonThrottle, SearchUserThrottle


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


# Public endpoint - anyone can browse artists
@api_view(['GET'])
@permission_classes([AllowAny])
def artists_endpoint(request):
    models = Artist.objects.all()
    serializer = ArtistSerializer(models, many=True)
    return Response(serializer.data)


# Protected endpoint - only admin users can upload to Arweave
@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_to_arweave_view(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    file = request.FILES.get('file')
    if not file:
        return Response({'success': False, 'error': 'No file provided'}, status=400)

    # Basic validation
    if file.size and file.size > 10 * 1024 * 1024:  # 10 MB hard cap (matches Weaviate cap)
        return Response({'success': False, 'error': 'File too large (max 10MB)'}, status=400)
    if file.content_type and not file.content_type.startswith('image/'):
        return Response({'success': False, 'error': 'Only image uploads are allowed'}, status=400)

    temp_path = None
    try:
        if hasattr(file, 'temporary_file_path'):
            temp_path = file.temporary_file_path()
        else:
            with NamedTemporaryFile(delete=False, suffix='.upload') as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name

        arweave_url = upload_to_arweave(temp_path)
        return Response({'success': True, 'url': arweave_url})
    except Exception as exc:
        return Response({'success': False, 'error': f'Upload failed: {exc}'}, status=500)
    finally:
        if temp_path and not hasattr(file, 'temporary_file_path') and os.path.exists(temp_path):
            os.remove(temp_path)


# Public endpoint - anyone can search by image (rate limited)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([SearchAnonThrottle, SearchUserThrottle])
def search_authors_by_image_data(request):
    image_file = request.FILES.get('image')
    limit = int(request.data.get('limit', 2))

    if image_file:
        # Read the file data into bytes
        image_data_bytes = image_file.read()

        similar_images = search_similar_authors_ids_by_image_data(image_data_bytes, limit)
        images_list = list(similar_images.objects)
        
        # Batch fetch all artworks and authors to avoid N+1 queries
        artwork_ids = [img.properties['artwork_psql_id'] for img in images_list]
        author_ids = [img.properties['author_psql_id'] for img in images_list]
        artworks = {a.id: a for a in Artwork.objects.filter(id__in=artwork_ids)}
        authors = {a.id: a for a in Artist.objects.filter(id__in=author_ids)}
        
        response_data = []
        for image in images_list:
            artwork = artworks.get(image.properties['artwork_psql_id'])
            author = authors.get(image.properties['author_psql_id'])
            if artwork and author:
                artwork_serializer = ArtworkSerializer(artwork)
                author_serializer = SearchArtistSerializer(author)
                response_data.append({
                    'artwork': artwork_serializer.data,
                    'author': author_serializer.data,
                })
        return Response(response_data)
    else:
        return Response({'error': 'Image data not provided'}, status=400)


# Public endpoint - anyone can search by image URL (rate limited)
@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([SearchAnonThrottle, SearchUserThrottle])
def search_authors_by_image_url(request):
    image_url = request.GET.get('image_url')
    limit = int(request.GET.get('limit', 1))
    similar_images = search_similar_authors_ids_by_image_url(image_url, limit)
    images_list = list(similar_images.objects)

    # Batch fetch all artworks and authors to avoid N+1 queries
    artwork_ids = [img.properties['artwork_psql_id'] for img in images_list]
    author_ids = [img.properties['author_psql_id'] for img in images_list]
    artworks = {a.id: a for a in Artwork.objects.filter(id__in=artwork_ids)}
    authors = {a.id: a for a in Artist.objects.filter(id__in=author_ids)}

    response_data = []
    for image in images_list:
        artwork = artworks.get(image.properties['artwork_psql_id'])
        author = authors.get(image.properties['author_psql_id'])

        if artwork and author:
            artwork_serializer = ArtworkSerializer(artwork)
            author_serializer = SearchArtistSerializer(author)
            response_data.append({
                'artwork': artwork_serializer.data,
                'author': author_serializer.data,
            })

    return Response(response_data)


# Public endpoint - anyone can search artworks by image (rate limited)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([SearchAnonThrottle, SearchUserThrottle])
def search_artworks_by_image_data(request):
    image_file = request.FILES.get('image')
    limit = int(request.data.get('limit', 10))

    if image_file:
        # Read the file data into bytes
        image_data_bytes = image_file.read()

        similar_images = search_similar_artwork_ids_by_image_data(image_data_bytes, limit)
        images_list = list(similar_images)
        
        # Batch fetch all artworks and authors to avoid N+1 queries
        artwork_ids = [img.properties['artwork_psql_id'] for img in images_list]
        author_ids = [img.properties['author_psql_id'] for img in images_list]
        artworks = {a.id: a for a in Artwork.objects.filter(id__in=artwork_ids)}
        authors = {a.id: a for a in Artist.objects.filter(id__in=author_ids)}
        
        response_data = []
        for image in images_list:
            artwork = artworks.get(image.properties['artwork_psql_id'])
            author = authors.get(image.properties['author_psql_id'])
            if artwork and author:
                artwork_serializer = ArtworkSerializer(artwork)
                author_serializer = SearchArtistSerializer(author)
                response_data.append({
                    'artwork': artwork_serializer.data,
                    'author': author_serializer.data,
                })
        return Response(response_data)
    else:
        return Response({'error': 'Image data not provided'}, status=400)


# Public endpoint - anyone can search artworks by image URL (rate limited)
@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([SearchAnonThrottle, SearchUserThrottle])
def search_artworks_by_image_url(request):
    image_url = request.GET.get('image_url')
    limit = int(request.GET.get('limit', 1))
    similar_images = search_similar_artwork_ids_by_image_url(image_url, limit)
    images_list = list(similar_images)

    # Batch fetch all artworks and authors to avoid N+1 queries
    artwork_ids = [img.properties['artwork_psql_id'] for img in images_list]
    author_ids = [img.properties['author_psql_id'] for img in images_list]
    artworks = {a.id: a for a in Artwork.objects.filter(id__in=artwork_ids)}
    authors = {a.id: a for a in Artist.objects.filter(id__in=author_ids)}

    response_data = []
    for image in images_list:
        artwork = artworks.get(image.properties['artwork_psql_id'])
        author = authors.get(image.properties['author_psql_id'])

        if artwork and author:
            artwork_serializer = ArtworkSerializer(artwork)
            author_serializer = SearchArtistSerializer(author)
            response_data.append({
                'artwork': artwork_serializer.data,
                'author': author_serializer.data,
            })

    return Response(response_data)

# http://localhost:8000/artists/search-artworks-by-image-url/?image_url=https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU&limit=1
