import weaviate
from artists.models import Artwork
from django.core.files.storage import default_storage
from artists.weaviate.weaviate import add_image_to_weaviete

# python -c "from artists.weaviate.data_helpers import add_all_artworks_to_weaviate;"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.data_helpers import add_all_artworks_to_weaviate;
add_all_artworks_to_weaviate()
"
'''
def add_all_artworks_to_weaviate():
    # weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    # artworks_weaviate = weaviete_client.collections.get("Artworks")
    print("Adding all artworks to Weaviate")
    artworks_psql = Artwork.objects.all()
    for artwork in artworks_psql:
        artwork_psql_id = artwork.id
        author_psql_id = artwork.artist.id
        arweave_image_url = artwork.picture_url
        picture_image_weaviate_id = artwork.picture_image_weaviate_id

        print("... picture_image_weaviate_id", picture_image_weaviate_id)
        # If the image is stored locally, get the absolute URL
        if not picture_image_weaviate_id and artwork.picture:
            print("--- arweave_image_url", arweave_image_url)
            # arweave_image_url = default_storage.url(artwork.picture.name)

            if arweave_image_url:
                uuid = add_image_to_weaviete(str(artwork_psql_id), str(author_psql_id), arweave_image_url)
                artwork.picture_image_weaviate_id = uuid
                artwork.save()