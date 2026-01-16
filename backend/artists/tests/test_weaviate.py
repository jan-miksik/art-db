"""Tests for Weaviate connection and integration."""
import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from ..models import Artwork, Artist
from .test_helpers import suppress_logger


class WeaviateConnectionFailureTests(TestCase):
    """Test Weaviate connection failure scenarios."""
    
    def setUp(self):
        self.client = Client()
        self.artist = Artist.objects.create(
            notes="Test",
            firstname="Test",
            surname="Artist",
            born=1985,
            gender="M",
            auctions_turnover_2023_h1_USD="100.00",
            profile_image_url="https://example.com/profile.png",
        )
        self.artwork = Artwork.objects.create(
            artist=self.artist,
            title="Test Work",
            picture="artworks/test.webp",
            picture_url="https://example.com/art.png",
            year=2020,
            sizeY=100,
            sizeX=100,
        )
    
    def test_weaviate_connection_failure_in_search(self):
        """Test that Weaviate connection failures are handled in search endpoints."""
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        url = reverse('search_artworks_by_image_data')
        
        # Mock the search function to raise an exception (simulating Weaviate failure)
        # The view doesn't catch exceptions, so it will return a 500 error
        with patch('artists.views.search_similar_artwork_ids_by_image_data') as mock_search:
            mock_search.side_effect = Exception("Weaviate connection failed")
            # The view will raise an unhandled exception with the default test client
            with suppress_logger('django.request'):
                with self.assertRaises(Exception):
                    self.client.post(url, {'image': file})
    
    def test_weaviate_client_context_manager_handles_exception(self):
        """Test that get_weaviate_client context manager properly handles exceptions."""
        from ..weaviate.client import get_weaviate_client
        import weaviate
        
        # Mock weaviate.connect_to_local to raise an exception
        with patch('artists.weaviate.client.weaviate.connect_to_local') as mock_connect:
            mock_connect.side_effect = Exception("Connection refused")

            # The context manager should raise the exception
            with suppress_logger('artists.weaviate.client'):
                with self.assertRaises(Exception):
                    with get_weaviate_client():
                        pass
    
    def test_weaviate_add_image_handles_connection_failure(self):
        """Test that add_image_to_weaviate handles connection failures with retries."""
        from ..weaviate.service import add_image_to_weaviate
        from unittest.mock import MagicMock
        
        # Mock get_weaviate_client to return a context manager that raises inside the with block
        # This simulates a connection failure that happens after connecting
        mock_client = MagicMock()
        mock_collections = MagicMock()
        # Make collections.get raise an exception (simulating connection failure)
        mock_collections.get.side_effect = Exception("Connection failed")
        mock_client.collections = mock_collections
        
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_client
        mock_context.__exit__.return_value = None
        
        # Mock url_to_base64 to avoid actual image download
        with patch('artists.weaviate.service.get_weaviate_client', return_value=mock_context):
            with patch('artists.weaviate.service.url_to_base64', return_value="base64string"):
                with patch('artists.weaviate.service.time.sleep'):  # Skip sleep delays
                    with suppress_logger('artists.weaviate.service', level=logging.CRITICAL):
                        # Should return None after all retries fail
                        result = add_image_to_weaviate(
                            artwork_psql_id=self.artwork.id,
                            author_psql_id=self.artist.id,
                            arweave_image_url="https://arweave.net/test"
                        )
                        self.assertIsNone(result)
