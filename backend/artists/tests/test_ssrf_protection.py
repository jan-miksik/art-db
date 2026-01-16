"""Tests for SSRF protection in Weaviate image URL handling."""
from django.test import TestCase
from unittest.mock import patch
import socket
import base64

from ..weaviate import (
    is_safe_url,
    url_to_base64,
)


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

        # Create actual valid PNG image bytes (not just header)
        from PIL import Image
        from io import BytesIO
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()

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
                # Use real Image.open with real image bytes - no need to mock it
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
