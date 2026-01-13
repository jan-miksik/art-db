import weaviate
from weaviate.classes.query import MetadataQuery
import base64
import requests
from urllib.parse import urlparse
import ipaddress
import socket
from weaviate.util import generate_uuid5  # Generate a deterministic ID
from weaviate.classes.query import Filter
from weaviate.classes.query import GroupBy
from weaviate import Client
import os
from PIL import Image
from io import BytesIO
import uuid
import time
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_weaviate_client():
    """Context manager for handling Weaviate client connections"""
    client = None
    try:
        client = weaviate.connect_to_local()
        yield client
    finally:
        if client is not None:
            client.close()


def resize_image_if_needed(base64_string, max_size_mb=10):
    """Resize the image if it's too large"""
    # Decode base64 to binary
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))

    # Calculate current size in MB
    current_size = len(img_data) / (1024 * 1024)

    if current_size > max_size_mb:
        # Calculate new dimensions to reduce size while maintaining aspect ratio
        ratio = (max_size_mb / current_size) ** 0.5
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)

        # Resize image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert back to base64
        buffered = BytesIO()
        img.save(buffered, format=img.format or 'JPEG', quality=85)
        return base64.b64encode(buffered.getvalue()).decode()

    return base64_string


def is_safe_url(url):
    """
    SECURITY: Validate URL to prevent SSRF attacks.
    Blocks requests to localhost, private networks, and non-HTTP(S) schemes.
    """
    try:
        parsed = urlparse(url)

        # Only allow http and https schemes
        if parsed.scheme not in ('http', 'https'):
            logger.warning(f"SSRF protection: Blocked non-HTTP scheme: {parsed.scheme}")
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Block localhost variations
        if hostname in ('localhost', '127.0.0.1', '0.0.0.0', '::1'):
            logger.warning(f"SSRF protection: Blocked localhost access: {hostname}")
            return False

        # Resolve hostname to IP and check if it's private
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                logger.warning(f"SSRF protection: Blocked private/reserved IP: {ip}")
                return False
        except (socket.gaierror, ValueError):
            # If we can't resolve, block it - unresolvable hosts are suspicious
            logger.warning(f"SSRF protection: Blocked unresolvable host: {hostname}")
            return False
        return True
    except Exception as e:
        logger.error(f"SSRF protection: URL validation error: {e}")
        return False


def url_to_base64(url, timeout=10):
    """
    Convert image URL to base64 with size checking.
    SECURITY: Includes SSRF protection and request timeout.
    """
    # Validate URL for SSRF protection
    if not is_safe_url(url):
        raise ValueError(f"URL blocked by security policy: {url}")

    # Make request with timeout and verify SSL
    response = requests.get(
        url,
        timeout=timeout,
        verify=True,
        headers={'User-Agent': 'ArtDB-ImageFetcher/1.0'}
    )
    response.raise_for_status()

    # Validate content type
    content_type = response.headers.get('content-type', '')
    if not content_type.startswith('image/'):
        raise ValueError(f"URL does not point to an image: {content_type}")

    # Convert to base64
    base64_string = base64.b64encode(response.content).decode()

    # Resize if needed
    return resize_image_if_needed(base64_string)


# def connect_to_weaviate():
#     return weaviate.connect_to_custom(
#         http_host=os.getenv("WEAVIATE_URL"),  # URL only, no http prefix
#         http_port=8080,
#         http_secure=True,   # Set to True if https
#         grpc_host=os.getenv("WEAVIATE_GPC_URL"),
#         grpc_port=50051,      # Default is 50051, WCD uses 443
#         grpc_secure=True,   # Edit as needed
#         auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
#     )


############################
# add image to weaviete
############################

def check_object_exists(artworks, obj_uuid):
    """Check if an object exists in Weaviate"""
    try:
        result = artworks.query.fetch_object_by_id(str(obj_uuid))
        return result is not None
    except:
        return False

def remove_if_exists(artworks, obj_uuid):
    """Remove object if it exists in Weaviate"""
    try:
        if check_object_exists(artworks, obj_uuid):
            artworks.data.delete_by_id(str(obj_uuid))
            print(f"Removing already existing object with UUID: {obj_uuid}")
            time.sleep(0.5)  # Give Weaviate time to process the deletion
    except Exception as e:
        print(f"Error removing existing object: {str(e)}")


def add_image_to_weaviete(artwork_psql_id, author_psql_id, arweave_image_url):
    print("[[[[[ add_image_to_weaviete ]]]]]")
    max_retries = 3
    current_try = 0

    while current_try < max_retries:
        with get_weaviate_client() as weaviate_client:
            try:
                artworks = weaviate_client.collections.get("Artworks")

                # Convert image to base64 with size handling
                try:
                    base64_string = url_to_base64(arweave_image_url)
                except Exception as e:
                    print(f"Error converting image to base64: {str(e)}")
                    return None

                data_properties = {
                    "artwork_psql_id": str(artwork_psql_id),
                    "author_psql_id": str(author_psql_id),
                    "image": base64_string
                }

                # Generate a deterministic ID, it will generate the same ID for the same data
                obj_uuid = generate_uuid5(data_properties)
                print(f"Adding image to Weaviate with UUID: {obj_uuid}")

                remove_if_exists(artworks, obj_uuid)

                uuid_str = artworks.data.insert(
                    properties=data_properties,
                    uuid=str(obj_uuid)
                )

                if check_object_exists(artworks, uuid_str):
                    print(f"Artwork {artwork_psql_id} successfully added to Weaviate with ID {uuid_str}")
                    return uuid_str

                print(f"Failed to verify artwork {artwork_psql_id} in Weaviate")
                return None

            except Exception as e:
                print(f"Attempt {current_try + 1} failed: {str(e)}")
                current_try += 1
                if current_try < max_retries:
                    time.sleep(2)  # Wait before retrying

    print(f"Failed to add artwork to Weaviate after {max_retries} attempts")
    return None

# python -c "from artists.weaviate.weaviate import add_image_to_weaviete; add_image_to_weaviete('25', '1', 'https://arweave.net/0zYEjsrKFVa-qt9k9pO7W7j1M-Xyzj_y4MeEq5NY1Hk')"


############################
# Search for similar authors
############################

def search_similar_authors_ids_by_base64(image_data_base64, limit=2):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")

    responses = artworks.query.near_image(
        near_image=image_data_base64,
        group_by=GroupBy(
            prop="author_psql_id",
            number_of_groups=limit,
            objects_per_group=1
        )
    )

    weaviate_client.close()
    return responses


def search_similar_authors_ids_by_image_data(image_data_bytes, limit=2):
    image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
    return search_similar_authors_ids_by_base64(image_data_base64, limit)


def search_similar_authors_ids_by_image_url(image_url, limit=2):
    image_data_base64 = url_to_base64(image_url)
    return search_similar_authors_ids_by_base64(image_data_base64, limit)


# ++++++++++++++++++++ #
# ++++++++++++++++++++ #
# ++++++++++++++++++++ #

############################
# add image to weaviete
############################

# Should be added?
# def add_image_to_weaviete_batch(artwork_psql_id, author_psql_id, arweave_image_url):
#     # _weaviate_client = weaviate.connect_to_local() # Connect with default parameters
#     # _artworks = weaviate_client.collections.get("Artworks")
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
#         weaviate_client.close()
#         return obj_uuid


# def add_image_vector_to_weaviete(image_file, arweave_link):
#     # Calculate the image vector using Weaviete
#     vector = weaviate_client.image.encode(image_file)

#     # Create a data object with the image properties
#     data = {
#         "vector": vector,
#         "artwork_psql_id": arweave_link
#     }

#     # Add the data object to Weaviete
#     weaviate_client.data_object.create(data, "Image")


############################
# Search for similar images
############################

def search_similar_artwork_ids_by_image_url(image_url, limit=1):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    base64_string = url_to_base64(image_url)

    # Perform query
    response = artworks.query.near_image(
        near_image=base64_string,
        # return_properties=["artwork_psql_id"],
        limit=limit
    )
    # print(response.objects[0])
    weaviate_client.close()
    return response.objects

# python -c "from artists.weaviate.weaviate import search_similar_artwork_ids_by_image_url; search_similar_artwork_ids_by_image_url('https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU');"


def search_similar_artwork_ids_by_image_data(image_data_bytes, limit=2):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    # Assuming image_data is in base64 format
    image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')

    response = artworks.query.near_image(
        near_image=image_data_base64,
        # return_properties=["artwork_psql_id"],
        limit=limit
    )
    weaviate_client.close()
    return response.objects


def search_similar_images_by_weaviate_image_id(weaviate_image_id, author_psql_id, limit=2):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    # Perform query
    response = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=limit,
        # filters=Filter.by_property("author_psql_id").not_equal(author_psql_id),
        return_metadata=MetadataQuery(distance=True)
    )
    # print(response.objects[0])
    weaviate_client.close()
    return response.objects


# python -c "from artists.weaviate.weaviate import search_similar_authors_by_weaviate_image_id; search_similar_authors_by_weaviate_image_id('9843a5ac-9563-52fc-b38f-8ae9c01da52f');"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.weaviate import search_similar_authors_by_weaviate_image_id
search_similar_authors_by_weaviate_image_id('2b265d11-20f9-55ba-9a2a-fbcdf89bdb07')
"
'''


def search_similar_authors_by_weaviate_image_id(weaviate_image_id, limit=5):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    responses = []
    filters = None

    for _ in range(limit):
        response = artworks.query.near_object(
            near_object=weaviate_image_id,
            limit=1,
            filters=filters,
            return_metadata=MetadataQuery(distance=True)
        )

        if response.objects:
            responses.append(response.objects[0])
            author_psql_id = response.objects[0].properties['author_psql_id']
            new_filter = Filter.by_property("author_psql_id").not_equal(author_psql_id)

            if filters is None:
                filters = new_filter
            else:
                filters = filters & new_filter

    weaviate_client.close()
    return responses

    # Perform query
    # initialResponse = artworks.query.near_object(
    #     near_object=weaviate_image_id,
    #     limit=1,
    #     # filters=Filter.by_property("author_psql_id").not_equal(author_psql_id),
    #     return_metadata=MetadataQuery(distance=True)
    # )

    # print('Initial Response ------', initialResponse.objects[0].properties['author_psql_id'])
    # # next queries,
    # nextResponse = artworks.query.near_object(
    #     near_object=weaviate_image_id,
    #     limit=1,
    #     filters=Filter.by_property("author_psql_id").not_equal(initialResponse.objects[0].properties['author_psql_id']),
    #     return_metadata=MetadataQuery(distance=True)
    # )

    # nextResponse2 = artworks.query.near_object(
    #     near_object=weaviate_image_id,
    #     limit=1,
    #     filters=Filter.by_property("author_psql_id").not_equal(initialResponse.objects[0].properties['author_psql_id']) &
    #         (Filter.by_property("author_psql_id").not_equal(nextResponse.objects[0].properties['author_psql_id'])),
    #     return_metadata=MetadataQuery(distance=True)
    # )

    # combined_responses = initialResponse.objects + nextResponse.objects + nextResponse2.objects

    # print('rrrrrrrrr', combined_responses)
    # weaviate_client.close()
    # return combined_responses


def search_similar_images_by_vector(query_vector, limit=2):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    # Perform query
    response = artworks.query.near_vector(
        near_vector=query_vector,  # your query vector goes here
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )
    # print(response.objects[0])
    weaviate_client.close()
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
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    print("Reading all artworks")
    artworks = weaviate_client.collections.get("Artworks")
    try:
        for item in artworks.iterator():
            print(item.uuid, item.properties)
        # Your code here
    finally:
        weaviate_client.close()


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
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    print("Reading image by ID")
    artworks = weaviate_client.collections.get("Artworks")
    try:
        data_object = artworks.query.fetch_object_by_id(image_id)
        print(data_object)
        return data_object
    finally:
        weaviate_client.close()


# e3a39360-aacc-5214-829a-4f23b8a8c3eb {'author_psql_id': '1', 'artwork_psql_id': '1'}
# python -c "from artists.weaviate.weaviate import remove_by_weaviate_id; remove_by_weaviate_id('8f422679-e269-510d-b04e-b87f4128f52c');"
'''
python -c "
import os
import django
django.setup()
from artists.weaviate.weaviate import remove_by_weaviate_id
remove_by_weaviate_id('e3a39360-aacc-5214-829a-4f23b8a8c3eb')
"
'''


def remove_by_weaviate_id(weaviate_id):
    weaviate_client = weaviate.connect_to_local()  # Connect with default parameters
    artworks = weaviate_client.collections.get("Artworks")
    print("Reading image by ID")
    artworks = weaviate_client.collections.get("Artworks")
    try:
        data_object = artworks.data.delete_by_id(weaviate_id)
        print(data_object)
        return data_object
    finally:
        weaviate_client.close()

# python -c "from artists.weaviate.weaviate import add_all_artworks_to_weaviate; add_all_artworks_to_weaviate();"
# def add_all_artworks_to_weaviate():
#     # weaviate_client = weaviate.connect_to_local() # Connect with default parameters
#     # artworks_weaviate = weaviate_client.collections.get("Artworks")
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
