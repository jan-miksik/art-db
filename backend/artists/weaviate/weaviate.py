import weaviate
from weaviate.classes.query import MetadataQuery
import base64, requests
from weaviate.util import generate_uuid5  # Generate a deterministic ID
from weaviate.classes.query import Filter
from artists.models import Artwork
# import os
# import django
# django.setup()


# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile

# weaviete_client = weaviate.connect_to_local() # Connect with default parameters
# artworks = weaviete_client.collections.get("Artworks")

def url_to_base64(url):
    image_response = requests.get(url)
    content = image_response.content
    return base64.b64encode(content).decode("utf-8")

############################
# add image to weaviete
############################

# Should be added?
# def add_image_to_weaviete_batch(artwork_psql_id, author_psql_id, arweave_image_url):
#     # _weaviete_client = weaviate.connect_to_local() # Connect with default parameters
#     # _artworks = weaviete_client.collections.get("Artworks")
#     base64_string = url_to_base64(arweave_image_url)

#     print("Adding image to Weaviate", base64_string)
#     data_properties = {
#         "artwork_psql_id": artwork_psql_id,
#         "author_psql_id": author_psql_id,
#         "image": base64_string
#     }
#     obj_uuid = generate_uuid5(data_properties)
#     print("Adding image to Weaviate", obj_uuid)
#     try:
#         with artworks.batch.dynamic() as batch:
#             batch.add_object(properties=data_properties, uuid=obj_uuid)
#     finally:
#         print("finally finally finally")
#         weaviete_client.close()
#         return obj_uuid

def add_image_to_weaviete(artwork_psql_id, author_psql_id, arweave_image_url):
    print("[[[[[ add_image_to_weaviete ]]]]]")
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    uuid = None

    try:
        base64_string = url_to_base64(arweave_image_url)
        data_properties = {
            "artwork_psql_id": artwork_psql_id,
            "author_psql_id": author_psql_id,
            "image": base64_string
        }
        # Generate a deterministic ID, it will generate the same ID for the same data
        obj_uuid = generate_uuid5(data_properties)
        print("Adding image to Weaviate", obj_uuid)
        uuid = artworks.data.insert(
            properties=data_properties,
            uuid=obj_uuid
        )

    finally:
        weaviete_client.close()
    
    return uuid

# python -c "from artists.weaviate.weaviate import add_image_to_weaviete; add_image_to_weaviete('25', '1', 'https://arweave.net/0zYEjsrKFVa-qt9k9pO7W7j1M-Xyzj_y4MeEq5NY1Hk')"

# python -c "from artists.weaviate.weaviate import add_image_to_weaviete; add_image_to_weaviete('11', '9', 'https://arweave.net/V7yA1C67Nj5goTDKjkW225xFq_NNZEDh4IS7TSfp-qw');"



# def add_image_vector_to_weaviete(image_file, arweave_link):
#     # Calculate the image vector using Weaviete
#     vector = weaviete_client.image.encode(image_file)

#     # Create a data object with the image properties
#     data = {
#         "vector": vector,
#         "artwork_psql_id": arweave_link
#     }

#     # Add the data object to Weaviete
#     weaviete_client.data_object.create(data, "Image")


############################
# Search for similar images
############################

def search_similar_artwork_ids_by_image_url(image_url, limit=1):
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    base64_string = url_to_base64(image_url)

    # Perform query
    response = artworks.query.near_image(
        near_image=base64_string,
        # return_properties=["artwork_psql_id"],
        limit=limit
    )
    # print(response.objects[0])
    weaviete_client.close()
    return response.objects


# python -c "from artists.weaviate.weaviate import search_similar_artwork_ids_by_image_url; search_similar_artwork_ids_by_image_url('https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU');"
def search_similar_artwork_ids_by_image_data(image_data_bytes, limit=2):
    weaviete_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    # Assuming image_data is in base64 format
    image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')

    response = artworks.query.near_image(
        near_image=image_data_base64,
        # return_properties=["artwork_psql_id"],
        limit=limit
    )
    weaviete_client.close()
    return response.objects


def search_similar_images_by_weaviate_image_id(weaviate_image_id, author_psql_id, limit=2):
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    # Perform query
    response = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=limit,
        # filters=Filter.by_property("author_psql_id").not_equal(author_psql_id),
        return_metadata=MetadataQuery(distance=True)
    )
    # print(response.objects[0])
    weaviete_client.close()
    return response.objects

# python -c "from artists.weaviate.weaviate import search_similar_authors_by_weaviate_image_id; search_similar_authors_by_weaviate_image_id('9843a5ac-9563-52fc-b38f-8ae9c01da52f');"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.weaviate import search_similar_authors_by_weaviate_image_id
search_similar_authors_by_weaviate_image_id('9843a5ac-9563-52fc-b38f-8ae9c01da52f')
"
'''
def search_similar_authors_by_weaviate_image_id(weaviate_image_id, limit=5):
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    # Perform query
    initialResponse = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=1,
        # filters=Filter.by_property("author_psql_id").not_equal(author_psql_id),
        return_metadata=MetadataQuery(distance=True)
    )

    print('Initial Response ------', initialResponse.objects[0].properties['author_psql_id'])
    # next queries,
    nextResponse = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=3,
        filters=Filter.by_property("author_psql_id").not_equal(initialResponse.objects[0].properties['author_psql_id']),
        return_metadata=MetadataQuery(distance=True)
    )

    combined_responses = initialResponse.objects + nextResponse.objects

    print('rrrrrrrrr', combined_responses)
    weaviete_client.close()
    return combined_responses


def search_similar_images_by_vector(query_vector, limit=2):
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    # Perform query
    response = artworks.query.near_vector(
        near_vector=query_vector, # your query vector goes here
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )
    # print(response.objects[0])
    weaviete_client.close()
    return response.objects

# python -c "from artists.weaviate.weaviate import read_all_artworks; read_all_artworks();"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.weaviate import read_all_artworks
read_all_artworks()
"
'''
def read_all_artworks():
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    print("Reading all artworks")
    artworks = weaviete_client.collections.get("Artworks")
    try:
        for item in artworks.iterator():
            print(item.uuid, item.properties)
        # Your code here
    finally:
        weaviete_client.close()

# python -c "from artists.weaviate.weaviate import get_image_by_weaviate_id; get_image_by_weaviate_id('021155da-fb99-5201-b240-9c9c46ec7965');"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.weaviate import get_image_by_weaviate_id
get_image_by_weaviate_id('498defaf-5b7e-52e4-ac96-ae2b5dcc278b')
"
'''
def get_image_by_weaviate_id(image_id):
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    print("Reading image by ID")
    artworks = weaviete_client.collections.get("Artworks")
    try:
        data_object = artworks.query.fetch_object_by_id(image_id)
        print(data_object)
        return data_object
    finally:
        weaviete_client.close()


# python -c "from artists.weaviate.weaviate import remove_by_weaviate_id; remove_by_weaviate_id('8f422679-e269-510d-b04e-b87f4128f52c');"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.weaviate import remove_by_weaviate_id
remove_by_weaviate_id('ab496144-d996-57a1-a200-8221208fb8e5')
"
'''
def remove_by_weaviate_id(weaviate_id):
    weaviete_client = weaviate.connect_to_local() # Connect with default parameters
    artworks = weaviete_client.collections.get("Artworks")
    print("Reading image by ID")
    artworks = weaviete_client.collections.get("Artworks")
    try:
        data_object = artworks.data.delete_by_id(weaviate_id)
        print(data_object)
        return data_object
    finally:
        weaviete_client.close()



# python -c "from artists.weaviate.weaviate import add_all_artworks_to_weaviate; add_all_artworks_to_weaviate();"
# def add_all_artworks_to_weaviate():
#     # weaviete_client = weaviate.connect_to_local() # Connect with default parameters
#     # artworks_weaviate = weaviete_client.collections.get("Artworks")
#     artworks_psql = Artwork.objects.all()
#     for artwork in artworks_psql:
#         artwork_psql_id = artwork.id
#         author_psql_id = artwork.artist.id
#         arweave_image_url = artwork.picture_url

        # If the image is stored locally, get the absolute URL
        # if not arweave_image_url and artwork.picture:
            # arweave_image_url = default_storage.url(artwork.picture.name)

            # if arweave_image_url:
            #     uuid = add_image_to_weaviete(artwork_psql_id, author_psql_id, arweave_image_url)
            #     artwork.picture_image_weaviate_id = uuid
            #     artwork.save()