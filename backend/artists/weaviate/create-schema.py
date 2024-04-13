import weaviate
import weaviate.classes.config as wvcc

client = weaviate.connect_to_local() # Connect with default parameters

schema = {
    "classes": [
        {
            "class": "Artworks",
            "description": "Images of artworks",
            "moduleConfig": {
                "img2vec-neural": {
                    "imageFields": [
                        "image"
                    ]
                }
            },
            "vectorIndexType": "hnsw", 
            "vectorizer": "img2vec-neural", # the img2vec-neural Weaviate module
            "properties": [
                {
                    "name": "artwork",
                    "dataType": ["string"],
                    "description": "name of the artwork",
                },
                {
                    "name": "author",
                    "dataType": ["string"],
                    "description": "name of the author",
                },
                {
                    "name": "arweave_link",
                    "dataType":["string"],
                    "description": "arweave link of the image",
                }
            ]
        }
    ]
}

# adding the schema 
client.schema.create(schema)


client = weaviate.connect_to_local()

try:
    # Note that you can use `client.collections.create_from_dict()` to create a collection from a v3-client-style JSON object
    collection = client.collections.create(
        name="TestArticle",
        vectorizer_config=wvcc.Configure.Vectorizer.text2vec_cohere(),
        generative_config=wvcc.Configure.Generative.cohere(),
        properties=[
            wvcc.Property(
                name="title",
                data_type=wvcc.DataType.TEXT
            )
        ]
    )

finally:
    client.close()

print("The schema has been defined.")