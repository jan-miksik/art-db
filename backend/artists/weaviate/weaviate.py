import weaviate

weaviete_client = weaviate.connect_to_local() # Connect with default parameters

def add_image_to_weaviete(artwork_name, author_name, arweave_link):

    # with client.batch as batch:
        # for encoded_file_path in os.listdir("./base64_images"):
        #     with open("./base64_images/" + encoded_file_path) as file:
        #         file_lines = file.readlines()

    data_properties = {
        "artwork": artwork_name,
        "author": author_name,
        "arweave_link": arweave_link,
    }

        # batch.add_data_object(data_properties, "Artworks")

    try:
        with weaviete_client.batch.dynamic() as batch:  # or <collection>.batch.dynamic()
            batch.add_object(properties=data_properties, collection="Artworks")

    finally:
        weaviete_client.close()


def search_similar_images(image_file, limit=5):
    # Calculate the image vector using Weaviete
    vector = weaviete_client.data_object.get_vector(image_file)

    # Search for similar images in Weaviete
    result = weaviete_client.data_object.get(
        class_name="Image",
        vector=vector,
        vector_use_product=True,
        limit=limit
    )

    # Process the results
    similar_images = []
    for res in result["data"]["get"]["data"]["Get"]["data"]["data"]:
        similar_images.append({
            "arweave_link": res["arweave_link"],
            "author": res["author"]
        })

    return similar_images


def add_image_vector_to_weaviete(image_file, author, arweave_link):
    # Calculate the image vector using Weaviete
    vector = weaviete_client.image.encode(image_file)

    # Create a data object with the image properties
    data = {
        "vector": vector,
        "author": author,
        "arweave_link": arweave_link
    }

    # Add the data object to Weaviete
    weaviete_client.data_object.create(data, "Image")

# client = weaviate.Client(WEAVIATE_URL)
# set_up_batch()
# add_image_to_weaviete()

# print("The objects have been uploaded to Weaviate.")