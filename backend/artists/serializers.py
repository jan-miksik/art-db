from rest_framework import serializers
from .models import Artist, Artwork


class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = [
            'id',
            'title',
            'picture_url',
            'year',
            'sizeX',
            'sizeY',
        ]  # add the fields you want to include


class ArtistSerializer(serializers.ModelSerializer):
    artworks = ArtworkSerializer(source='artwork_set', many=True, read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id',
            'firstname',
            'surname',
            'name',
            'notes',
            'profile_image_url',
            'artworks',
            'born',
            'gender',
            'auctions_turnover_2023_h1_USD',
            'similar_authors_postgres_ids',
            'media_types',
        ]


class SearchArtistSerializer(serializers.ModelSerializer):
    """Lightweight serializer for search results - excludes nested artworks to avoid N+1 queries"""
    
    class Meta:
        model = Artist
        fields = [
            'id',
            'firstname',
            'surname',
            'name',
            'notes',
            'profile_image_url',
            'born',
            'gender',
            'auctions_turnover_2023_h1_USD',
            'similar_authors_postgres_ids',
            'media_types',
        ]
