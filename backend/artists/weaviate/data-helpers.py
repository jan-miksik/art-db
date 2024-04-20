import weaviate
from artists.models import Artwork
from django.core.files.storage import default_storage
from artists.weaviate.weaviate import add_image_to_weaviete

# python -c "from artists.weaviate.data-helpers import add_all_artworks_to_weaviate; add_all_artworks_to_weaviate();"
def add_all_artworks_to_weaviate():
    # weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    # artworks_weaviate = weaviete_client.collections.get("Artworks")
    artworks_psql = Artwork.objects.all()
    for artwork in artworks_psql:
        artwork_psql_id = artwork.id
        author_psql_id = artwork.artist.id
        arweave_image_url = artwork.picture_url

        # If the image is stored locally, get the absolute URL
        if not arweave_image_url and artwork.picture:
            arweave_image_url = default_storage.url(artwork.picture.name)

            if arweave_image_url:
                uuid = add_image_to_weaviete(artwork_psql_id, author_psql_id, arweave_image_url)
                artwork.picture_image_weaviate_id = uuid
                artwork.save()