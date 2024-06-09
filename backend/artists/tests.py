from django.test import TestCase, Client
from .models import Artwork, Artist
from .weaviate.weaviate import add_image_to_weaviete
from django.urls import reverse
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

        def url_to_base64(url):
            image_response = requests.get(url)
            content = image_response.content
            return base64.b64encode(content).decode("utf-8")

        image_url = 'https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU'
        image_data = url_to_base64(image_url)
        payload = {
            'image': image_data,
            'limit': 2
        }
        url = reverse('search_artworks_by_image_data')
        response = client.post(url, data=payload, content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the response data
