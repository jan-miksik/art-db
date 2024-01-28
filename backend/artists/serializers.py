from rest_framework import serializers
from .models import Artist, Artwork

class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = ['id', 'title', 'picture']  # add the fields you want to include

class ArtistSerializer(serializers.ModelSerializer):
    artworks = ArtworkSerializer(source='artwork_set', many=True, read_only=True)

    class Meta:
        model = Artist
        fields = ['id', 'name', 'notes', 'profile_image', 'artworks']