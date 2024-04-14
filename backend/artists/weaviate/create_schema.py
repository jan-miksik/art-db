import weaviate
import weaviate
import weaviate.classes as wvc

def create_schema():
    try:
        client = weaviate.connect_to_local()
        client.collections.delete(["Artworks"])

        artworks = client.collections.create(
            name="Artworks",
            properties=[
                wvc.config.Property(
                    name="artwork_psql_id",
                    data_type=wvc.config.DataType.TEXT,
                    description="id of the artwork in posgresql",
                ),
                wvc.config.Property(
                    name="image",
                    data_type=wvc.config.DataType.BLOB,
                    description="image",
                ),
            ],
            # the img2vec-neural Weaviate module
            vectorizer_config=wvc.config.Configure.Vectorizer.img2vec_neural(image_fields=["image"]),
            # vector_index_type=VectorIndexType.HNSW
        )

        print('artworks: ', artworks)

        schema = client.collections.list_all(simple=False)  # Use `simple=False` to get comprehensive information
        print(schema)
    finally:
        client.close()

# python -c "from artists.weaviate.create_schema import create_schema; create_schema()"