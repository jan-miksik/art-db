import weaviate
from weaviate.classes.query import MetadataQuery
import base64, requests

weaviete_client = weaviate.connect_to_local() # Connect with default parameters
artworks = weaviete_client.collections.get("Artworks")

def url_to_base64(url):
    image_response = requests.get(url)
    content = image_response.content
    return base64.b64encode(content).decode("utf-8")

############################
# add image to weaviete
############################

def add_image_to_weaviete(artwork_psql_id, arweave_image_url):
    base64_string = url_to_base64(arweave_image_url)

    data_properties = {
        "artwork_psql_id": artwork_psql_id,
        "image": base64_string
    }
    try:
        with artworks.batch.dynamic() as batch:
            batch.add_object(properties=data_properties)
    finally:
        # os.remove(local_image_path)
        weaviete_client.close()


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

def search_similar_images_by_base64(image_url, limit=2):
    base64_string = url_to_base64(image_url)

    # Perform query
    response = artworks.query.near_image(
        near_image=base64_string,
        return_properties=["artwork_psql_id image"],
        limit=limit
    )
    print(response.objects[0])
    weaviete_client.close()
    return response.objects


def search_similar_images_by_weaviate_image_id(weaviate_image_id, limit=2):
    # Perform query
    response = artworks.query.near_object(
        near_object=weaviate_image_id,
        limit=limit,
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
