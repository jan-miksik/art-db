from rest_framework import viewsets
from .serializers import ArtistSerializer, ArtworkSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from artists.arweave_storage import upload_to_arweave
from django.shortcuts import get_object_or_404
from .weaviate.weaviate import search_similar_artwork_ids_by_image_url, search_similar_artwork_ids_by_image_data, \
    search_similar_authors_ids_by_image_data, search_similar_authors_ids_by_image_url
from .models import Artwork, Artist


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
    if file:
        file_path = file.temporary_file_path()
        arweave_url = upload_to_arweave(file_path)
        return Response({'success': True, 'url': arweave_url})
    return Response({'success': False, 'error': 'No file provided'}, status=400)


# Public endpoint - anyone can search by image
@api_view(['POST'])
@permission_classes([AllowAny])
def search_authors_by_image_data(request):
    image_file = request.FILES.get('image')
    limit = int(request.data.get('limit', 2))

    if image_file:
        # Read the file data into bytes
        image_data_bytes = image_file.read()

        similar_images = search_similar_authors_ids_by_image_data(image_data_bytes, limit)
        response_data = []
        for image in similar_images.objects:
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


# Public endpoint - anyone can search by image URL
@api_view(['GET'])
@permission_classes([AllowAny])
def search_authors_by_image_url(request):
    image_url = request.GET.get('image_url')
    limit = int(request.GET.get('limit', 1))
    similar_images = search_similar_authors_ids_by_image_url(image_url, limit)

    response_data = []
    for image in similar_images.objects:
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


# Public endpoint - anyone can search artworks by image
@api_view(['POST'])
@permission_classes([AllowAny])
def search_artworks_by_image_data(request):
    image_file = request.FILES.get('image')
    limit = int(request.data.get('limit', 10))

    if image_file:
        # Read the file data into bytes
        image_data_bytes = image_file.read()

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


# Public endpoint - anyone can search artworks by image URL
@api_view(['GET'])
@permission_classes([AllowAny])
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
