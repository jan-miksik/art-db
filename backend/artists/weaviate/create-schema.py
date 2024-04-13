import weaviate

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
                    "name": "artwork_psql_id",
                    "dataType": ["string"],
                    "description": "id of the artwork in posgresql",
                },
                {
                    "name": "image",
                    "dataType": ["blob"],
                    "description": "blob of the image",
                },
            ]
        }
    ]
}

# adding the schema 
# client.schema.create(schema)


client = weaviate.connect_to_local()
client.collections.create_from_dict(schema)

print("The schema has been defined.")