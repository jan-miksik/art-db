from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from io import BytesIO
import socket
import base64
import requests
from PIL import Image

from .models import Artwork, Artist
from .weaviate import (
    is_safe_url,
    resize_image_if_needed,
    url_to_base64,
    WeaviateImageError,
)


class SearchArtworksByImageURLTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.maxDiff = None  # Add this line

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

class DummyImage:
    """Mimics the weaviate response object shape"""
    def __init__(self, artwork_id, author_id):
        self.properties = {
            "artwork_psql_id": artwork_id,
            "author_psql_id": author_id,
        }


class SSRFProtectionTests(TestCase):
    def test_is_safe_url_returns_pinned_tuple(self):
        # Use a public-looking IP to avoid private/rfc1918 rejection
        with patch('artists.weaviate.service.socket.getaddrinfo') as mock_gai:
            mock_gai.return_value = [
                (socket.AF_INET, None, None, None, ('93.184.216.34', 443))
            ]
            result = is_safe_url("https://example.com/resource.png")
        self.assertEqual(result, ('example.com', '93.184.216.34', 443))

    def test_url_to_base64_uses_pinned_ip_and_host_header(self):
        # Prepare pinned validation result to ensure the same IP is reused
        pinned = ('example.com', '93.184.216.34', 443)

        # Fake image bytes for the happy path
        image_bytes = b"\x89PNG\r\n\x1a\n"  # PNG header bytes

        class DummyResponse:
            def __init__(self):
                self.status_code = 200
                self.headers = {'content-type': 'image/png'}
                self.closed = False

            def raise_for_status(self):
                return None

            def iter_content(self, chunk_size=8192):
                # Return all content in a single chunk
                yield image_bytes

            def close(self):
                self.closed = True

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.close()
                return False

        class DummySession:
            def __init__(self):
                self.mounted = []
                self.last_get_args = None
                self.last_get_kwargs = None

            def mount(self, prefix, adapter):
                self.mounted.append((prefix, adapter))

            def get(self, *args, **kwargs):
                self.last_get_args = args
                self.last_get_kwargs = kwargs
                self.last_response = DummyResponse()
                return self.last_response

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

        with patch('artists.weaviate.service.is_safe_url', return_value=pinned):
            with patch('artists.weaviate.service.requests.Session', return_value=DummySession()) as mock_session_cls:
                with patch('artists.weaviate.service.Image.open') as mock_open:
                    mock_open.return_value.__enter__.return_value.verify.return_value = None
                    result = url_to_base64("https://example.com/resource.png", timeout=5)

        # Ensure session was constructed
        mock_session_cls.assert_called_once()

        # Inspect the session we returned
        session_instance = mock_session_cls.return_value
        self.assertTrue(session_instance.mounted)
        mount_prefix, _ = session_instance.mounted[0]
        self.assertIn("93.184.216.34", mount_prefix)

        # The request should target the pinned IP in the URL while preserving Host header
        called_url = session_instance.last_get_args[0]
        called_headers = session_instance.last_get_kwargs["headers"]
        self.assertIn("93.184.216.34", called_url)
        self.assertEqual(called_headers["Host"], "example.com")

        # Base64 result should match the fake payload
        self.assertEqual(result, base64.b64encode(image_bytes).decode())

        # Response should be closed after streaming
        self.assertTrue(session_instance.last_response.closed)


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



class ResizeImageIfNeededTests(TestCase):
    def _make_base64_image(self, size=(200, 200), mode="RGBA", format="PNG"):
        img = Image.new(mode, size, color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format=format)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode(), img_bytes, img.size

    def test_shrinks_and_converts_to_rgb_with_min_dimension_clamp(self):
        b64_image, img_bytes, original_size = self._make_base64_image(size=(320, 240))
        max_size_mb = (len(img_bytes) / (1024 * 1024)) * 0.4  # force shrink

        result = resize_image_if_needed(b64_image, max_size_mb=max_size_mb)

        decoded = base64.b64decode(result)
        self.assertLessEqual(len(decoded), int(max_size_mb * 1024 * 1024))

        with Image.open(BytesIO(decoded)) as img:
            self.assertEqual(img.mode, "RGB")  # alpha removed
            self.assertGreater(img.width, 0)
            self.assertGreater(img.height, 0)
            self.assertLessEqual(img.width, original_size[0])
            self.assertLessEqual(img.height, original_size[1])

    def test_decompression_bomb_guard_raises(self):
        b64_image, img_bytes, _ = self._make_base64_image(size=(100, 100))
        max_size_mb = (len(img_bytes) / (1024 * 1024)) * 0.5  # ensure processing

        with patch('artists.weaviate.service.MAX_IMAGE_PIXELS', 10):
            with self.assertRaises(WeaviateImageError):
                resize_image_if_needed(b64_image, max_size_mb=max_size_mb)

