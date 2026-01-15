"""Tests for Arweave upload functionality and failure handling."""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from ..models import Artist
from .test_helpers import suppress_logger


class ArweaveUploadFailureTests(TestCase):
    """Test Arweave upload failure scenarios."""
    
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
    
    def test_arweave_upload_failure_returns_500(self):
        """Test that Arweave upload failures are handled gracefully."""
        self.client.force_login(self.admin_user)
        url = reverse('upload_to_arweave', kwargs={'pk': self.artist.pk})
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Mock upload_to_arweave to raise an exception
        with patch('artists.views.upload_to_arweave') as mock_upload:
            mock_upload.side_effect = Exception("Arweave connection failed")
            with suppress_logger('django.request'), suppress_logger('root'):
                response = self.client.post(url, {'file': file})
        
        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 'Upload failed')
    
    def test_arweave_upload_wallet_error(self):
        """Test handling of wallet-related errors during Arweave upload."""
        self.client.force_login(self.admin_user)
        url = reverse('upload_to_arweave', kwargs={'pk': self.artist.pk})
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Mock upload_to_arweave to raise a wallet-specific error
        with patch('artists.views.upload_to_arweave') as mock_upload:
            mock_upload.side_effect = FileNotFoundError("Wallet file not found")
            with suppress_logger('django.request'), suppress_logger('root'):
                response = self.client.post(url, {'file': file})
        
        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 'Upload failed')
    
    def test_arweave_upload_network_error(self):
        """Test handling of network errors during Arweave upload."""
        self.client.force_login(self.admin_user)
        url = reverse('upload_to_arweave', kwargs={'pk': self.artist.pk})
        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        
        # Mock upload_to_arweave to raise a network error
        with patch('artists.views.upload_to_arweave') as mock_upload:
            import requests
            mock_upload.side_effect = requests.exceptions.ConnectionError("Network unreachable")
            with suppress_logger('django.request'), suppress_logger('root'):
                response = self.client.post(url, {'file': file})
        
        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertFalse(body['success'])
