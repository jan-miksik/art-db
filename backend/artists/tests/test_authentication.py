"""Tests for authentication and authorization."""
import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from ..models import Artist
from .test_helpers import suppress_logger


class AuthenticationAuthorizationTests(TestCase):
    """Test authentication and authorization on protected endpoints."""
    
    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user (non-admin)
        self.regular_user = User.objects.create_user(
            username='user',
            password='testpass123',
            is_staff=False,
            is_superuser=False
        )
        
        # Create test artist
        self.artist = Artist.objects.create(
            notes="Test",
            firstname="Test",
            surname="Artist",
            born=1985,
            gender="M",
            auctions_turnover_2023_h1_USD="100.00",
        )
    
    def test_upload_to_arweave_requires_authentication(self):
        """Test that upload endpoint requires authentication."""
        url = reverse('upload_to_arweave', kwargs={'pk': self.artist.pk})
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Unauthenticated request should be denied
        with suppress_logger('django.request', level=logging.ERROR):
            response = self.client.post(url, {'file': file})
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_upload_to_arweave_requires_admin(self):
        """Test that upload endpoint requires admin privileges."""
        url = reverse('upload_to_arweave', kwargs={'pk': self.artist.pk})
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Login as regular (non-admin) user
        self.client.force_login(self.regular_user)
        
        # Should be denied
        with suppress_logger('django.request', level=logging.ERROR):
            response = self.client.post(url, {'file': file})
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_upload_to_arweave_allows_admin(self):
        """Test that admin users can access upload endpoint."""
        url = reverse('upload_to_arweave', kwargs={'pk': self.artist.pk})
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Mock successful upload
        with patch('artists.views.upload_to_arweave', return_value="https://arweave.net/test123"):
            response = self.client.post(url, {'file': file})
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['url'], "https://arweave.net/test123")
    
    def test_public_endpoints_allow_anonymous(self):
        """Test that public endpoints (like search) allow anonymous access."""
        url = reverse('search_artworks_by_image_data')
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Mock search to return empty results
        with patch('artists.views.search_similar_artwork_ids_by_image_data', return_value=[]):
            response = self.client.post(url, {'image': file})
        
        # Should succeed (200) even without authentication
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['success'])
