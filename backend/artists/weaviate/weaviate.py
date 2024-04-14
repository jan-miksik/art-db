import weaviate
from weaviate.classes.query import MetadataQuery
import base64, requests
from weaviate.util import generate_uuid5  # Generate a deterministic ID
from weaviate.classes.query import Filter

weaviete_client = weaviate.connect_to_local() # Connect with default parameters
artworks = weaviete_client.collections.get("Artworks")

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
    uuid = None

    try:
        base64_string = url_to_base64(arweave_image_url)
        data_properties = {
            "artwork_psql_id": artwork_psql_id,
            "author_psql_id": author_psql_id,
            "image": base64_string
        }
        obj_uuid = generate_uuid5(data_properties)
        print("Adding image to Weaviate", obj_uuid)
        uuid = artworks.data.insert(
            properties=data_properties,
            uuid=obj_uuid
        )

    finally:
        weaviete_client.close()
    
    return uuid

# python -c "from artists.weaviate.weaviate import add_image_to_weaviete; add_image_to_weaviete('25', '1', 'https://arweave.net/0zYEjsrKFVa-qt9k9pO7W7j1M-Xyzj_y4MeEq5NY1Hk'})"

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

def search_similar_images_by_image_url(image_url, limit=1):
    base64_string = url_to_base64(image_url)

    # Perform query
    response = artworks.query.near_image(
        near_image=base64_string,
        # return_properties=["artwork_psql_id"],
        limit=limit
    )
    print(response.objects[0])
    weaviete_client.close()
    return response.objects

# python -c "from artists.weaviate.weaviate import search_similar_images_by_base64; search_similar_images_by_base64('https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU');"

def search_similar_images_by_weaviate_image_id(weaviate_image_id, author_psql_id, limit=2):
    # Perform query
    response = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=limit,
        # filters=Filter.by_property("author_psql_id").not_equal(author_psql_id),
        return_metadata=MetadataQuery(distance=True)
    )
    print(response.objects[0])
    weaviete_client.close()
    return response.objects


def search_similar_authors_by_weaviate_image_id(weaviate_image_id, author_psql_id, limit=2):
    # Perform query
    response = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=limit,
        # filters=Filter.by_property("author_psql_id").not_equal(author_psql_id),
        return_metadata=MetadataQuery(distance=True)
    )
    print(response.objects[0])
    weaviete_client.close()
    return response.objects


def search_similar_images_by_vector(query_vector, limit=2):
    # Perform query
    response = artworks.query.near_vector(
        near_vector=query_vector, # your query vector goes here
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )
    print(response.objects[0])
    weaviete_client.close()
    return response.objects

# python -c "from artists.weaviate.weaviate import read_all_artworks; read_all_artworks();"
def read_all_artworks():
    print("Reading all artworks")
    artworks = weaviete_client.collections.get("Artworks")
    try:
        for item in artworks.iterator():
            print(item.uuid, item.properties)
        # Your code here
    finally:
        weaviete_client.close()

# python -c "from artists.weaviate.weaviate import get_image_by_id; get_image_by_id('8f422679-e269-510d-b04e-b87f4128f52c');"
def get_image_by_id(image_id):
    print("Reading image by ID")
    artworks = weaviete_client.collections.get("Artworks")
    try:
        data_object = artworks.query.fetch_object_by_id(image_id)
        print(data_object)
    finally:
        weaviete_client.close()




# def search_similar_images_by_arweave_image_url(arweave_image_url, limit=2):
#     # Download the image from Arweave
#     # response = requests.get(arweave_image_url)
#     # # Save the image to a local file
#     # local_image_path = "./search-image.jpg"
#     # with open(local_image_path, "wb") as f:
#     #     f.write(response.content)
#     # Send a HEAD request to get the response headers
#     head_response = requests.head(arweave_image_url)

#     # Get the file extension from the Content-Type header
#     content_type = head_response.headers.get('Content-Type', '')
#     file_extension = '.' + content_type.split('/')[-1]

#     # Save the image to a temporary local file
#     local_image_path = f"./temp_image{file_extension}"
#     with open(local_image_path, "wb") as f:
#         image_response = requests.get(arweave_image_url)
#         f.write(image_response.content)
#     try:
#         # Use the local file path with the Path object
#         # artworks = weaviete_client.collections.get("Artworks")
#         response = artworks.query.near_image(
#             near_image=Path(local_image_path),
#             # return_properties=["breed"],
#             limit=limit
#         )
#         print(response.objects[0])
#     finally:
#         weaviete_client.close()
#         # Remove the temporary local file
#         os.remove(local_image_path)
#     return response.objects
