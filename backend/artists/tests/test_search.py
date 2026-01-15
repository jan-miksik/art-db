"""Tests for search functionality."""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from ..models import Artwork, Artist
from .test_helpers import DummyImage


class SearchArtworksByImageURLTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.maxDiff = None

        # Create some test data if necessary
        self.artist = Artist.objects.create(
            notes="TBD",
            profile_image="image_181.png",
            firstname="Doron",
            surname="LANGBERG",
            born=1985,
            gender="M",
            auctions_turnover_2023_h1_USD="472991.00",
            profile_image_url="https://arweave.net/jrv8kfPn-THBUq5_WKRLym_R5h7BYy4JWMMF-ATwt3I",
        )
        self.artwork = Artwork.objects.create(
            artist=self.artist,
            title="Drawing Mike (diptych)",
            picture="artworks/Drawing_Mike_diptych_2020_203x244cm.webp",
            picture_url="https://arweave.net/0zYEjsrKFVa-qt9k9pO7W7j1M-Xyzj_y4MeEq5NY1Hk",
            year=2020,
            sizeY=203,
            sizeX=244,
        )


class SearchArtworksByImageDataTestCase(TestCase):
    def test_search_artworks_by_image_data(self):
        client = Client()

        # Create minimal artist/artwork to satisfy response serialization
        artist = Artist.objects.create(
            notes="TBD",
            profile_image="image_181.png",
            firstname="Test",
            surname="Artist",
            born=1985,
            gender="M",
            auctions_turnover_2023_h1_USD="100.00",
            profile_image_url="https://example.com/profile.png",
        )
        artwork = Artwork.objects.create(
            artist=artist,
            title="Test Work",
            picture="artworks/test.webp",
            picture_url="https://example.com/art.png",
            year=2020,
            sizeY=100,
            sizeX=100,
        )

        dummy_results = [DummyImage(artwork.id, artist.id)]

        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        url = reverse('search_artworks_by_image_data')

        with patch('artists.views.search_similar_artwork_ids_by_image_data', return_value=dummy_results):
            response = client.post(url, {'image': file, 'limit': 2})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['success'])
        self.assertIsNone(body['error'])
        data = body['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['artwork']['id'], artwork.id)
        self.assertEqual(data[0]['author']['id'], artist.id)


class N1QueryFixTestCase(TestCase):
    """Test that the N+1 query fix works correctly - should use only 2 queries regardless of result count"""
    
    def setUp(self):
        # Create multiple artists and artworks
        self.artists = []
        self.artworks = []
        for i in range(10):
            artist = Artist.objects.create(
                notes=f"Artist {i}",
                profile_image=f"image_{i}.png",
                firstname=f"First{i}",
                surname=f"Last{i}",
                born=1980 + i,
                gender="M",
                auctions_turnover_2023_h1_USD="100.00",
                profile_image_url=f"https://example.com/profile{i}.png",
            )
            self.artists.append(artist)
            
            artwork = Artwork.objects.create(
                artist=artist,
                title=f"Artwork {i}",
                picture=f"artworks/art{i}.webp",
                picture_url=f"https://example.com/art{i}.png",
                year=2020,
                sizeY=100,
                sizeX=100,
            )
            self.artworks.append(artwork)

    def test_search_artworks_batch_queries(self):
        """Verify that searching 10 results only makes 2 DB queries (not 20)"""
        client = Client()
        
        # Create dummy results for all 10 artworks
        dummy_results = [
            DummyImage(self.artworks[i].id, self.artists[i].id)
            for i in range(10)
        ]
        
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        url = reverse('search_artworks_by_image_data')
        
        with patch('artists.views.search_similar_artwork_ids_by_image_data', return_value=dummy_results):
            # Should only make 2 queries: one for Artwork, one for Artist
            with self.assertNumQueries(2):
                response = client.post(url, {'image': file, 'limit': 10})
        
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['success'])
        self.assertIsNone(body['error'])
        data = body['data']
        self.assertEqual(len(data), 10)
