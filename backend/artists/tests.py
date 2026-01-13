from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import Artwork, Artist
from .weaviate.weaviate import add_image_to_weaviete
import base64, requests


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
        # add_image_to_weaviete(str(self.artwork.pk), str(self.artist.pk), self.artwork.picture_url)


#     def test_search_artworks_by_image_url(self):
#         response = self.client.get('/artists/search-artworks-by-image-url/', {'image_url': 'https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU', 'limit': 1})

#         self.assertEqual(response.status_code, 200)

#         # TODO: resolve this assertion
#         # Check that the response data is correct
#         # This will depend on the format of your response data
#         # print(response.json())
#         # self.assertEqual(response.json(), [
#           #   {
#           #   'artist':
#           #       {
#           #         'auctions_turnover_2023_h1_USD': '472991.00',
#           #         'born': 1985,
#           #         'firstname': 'Doron',
#           #         'gender': 'M',
#           #         'id': 1,
#           #         'notes': 'TBD',
#           #         'profile_image': 'image_181.png',
#           #         'profile_image_url': 'https://arweave.net/jrv8kfPn-THBUq5_WKRLym_R5h7BYy4JWMMF-ATwt3I',
#           #         'surname': 'LANGBERG'
#           #       },
#           #   'artwork':
#           #     {
#           #       'artist': 1,
#           #       'id': 25,
#           #       'picture': 'artworks/Drawing_Mike_diptych_2020_203x244cm.webp',
#           #       'picture_url': 'https://arweave.net/0zYEjsrKFVa-qt9k9pO7W7j1M-Xyzj_y4MeEq5NY1Hk',
#           #       'sizeX': 244,
#           #       'sizeY': 203,
#           #       'title': 'Drawing Mike (diptych)',
#           #       'year': 2020
#           #   }
#           # }
#           # ])

# client = Client()
# image_url = 'https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU'
# limit = 1
# response = client.get(reverse('search_artworks_by_image_url'), {'image_url': image_url, 'limit': limit})
# print(response.data)

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

        # Dummy result object mimicking the weaviate response shape
        class DummyImage:
            def __init__(self, artwork_id, author_id):
                self.properties = {
                    "artwork_psql_id": artwork_id,
                    "author_psql_id": author_id,
                }

        dummy_results = [DummyImage(artwork.id, artist.id)]

        file = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        url = reverse('search_artworks_by_image_data')

        with patch('artists.views.search_similar_artwork_ids_by_image_data', return_value=dummy_results):
            response = client.post(url, {'image': file, 'limit': 2})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['artwork']['id'], artwork.id)
        self.assertEqual(data[0]['author']['id'], artist.id)
