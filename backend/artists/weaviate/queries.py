"""Query functions for Weaviate operations."""
import base64
import logging
from weaviate.classes.query import MetadataQuery, Filter, GroupBy

from .client import get_weaviate_client
from .service import url_to_base64
from .exceptions import WeaviateConnectionError

logger = logging.getLogger(__name__)


def search_similar_authors_ids_by_base64(image_data_base64, limit=2):
    """Search for similar authors by base64 image data."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            return artworks.query.near_image(
                near_image=image_data_base64,
                group_by=GroupBy(
                    prop="author_psql_id",
                    number_of_groups=limit,
                    objects_per_group=1
                )
            )
    except Exception as e:
        logger.error(f"Error searching similar authors by base64: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_authors_ids_by_image_data(image_data_bytes, limit=2):
    """Search for similar authors by image data bytes."""
    try:
        image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
        return search_similar_authors_ids_by_base64(image_data_base64, limit)
    except WeaviateConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error searching similar authors by image data: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_authors_ids_by_image_url(image_url, limit=2):
    """Search for similar authors by image URL."""
    try:
        image_data_base64 = url_to_base64(image_url)
        return search_similar_authors_ids_by_base64(image_data_base64, limit)
    except WeaviateConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error searching similar authors by image URL: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_artwork_ids_by_image_url(image_url, limit=1):
    """Search for similar artworks by image URL."""
    try:
        base64_string = url_to_base64(image_url)
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            response = artworks.query.near_image(
                near_image=base64_string,
                limit=limit
            )
            return response.objects
    except Exception as e:
        logger.error(f"Error searching similar artworks by image URL: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_artwork_ids_by_image_data(image_data_bytes, limit=2):
    """Search for similar artworks by image data bytes."""
    try:
        image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            response = artworks.query.near_image(
                near_image=image_data_base64,
                limit=limit
            )
            return response.objects
    except Exception as e:
        logger.error(f"Error searching similar artworks by image data: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_images_by_weaviate_image_id(weaviate_image_id, limit=2):
    """Search for similar images by Weaviate image ID."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            response = artworks.query.near_object(
                near_object=weaviate_image_id,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )
            return response.objects
    except Exception as e:
        logger.error(f"Error searching similar images by Weaviate ID: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_authors_by_weaviate_image_id(weaviate_image_id, limit=5):
    """Search for similar authors by Weaviate image ID, excluding duplicates."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            grouped = GroupBy(
                prop="author_psql_id",
                number_of_groups=limit,
                objects_per_group=1
            )

            try:
                grouped_response = artworks.query.near_object(
                    near_object=weaviate_image_id,
                    group_by=grouped,
                    return_metadata=MetadataQuery(distance=True)
                )
                if grouped_response.objects:
                    return grouped_response.objects
            except TypeError:
                # Fallback for clients without group_by support on near_object
                pass

            responses = []
            filters = None

            for _ in range(limit):
                response = artworks.query.near_object(
                    near_object=weaviate_image_id,
                    limit=1,
                    filters=filters,
                    return_metadata=MetadataQuery(distance=True)
                )

                if not response.objects:
                    break

                first_object = response.objects[0]
                responses.append(first_object)
                author_psql_id = first_object.properties.get("author_psql_id")
                if author_psql_id is None:
                    continue

                new_filter = Filter.by_property("author_psql_id").not_equal(author_psql_id)
                filters = new_filter if filters is None else filters & new_filter

            return responses
    except Exception as e:
        logger.error(f"Error searching similar authors by Weaviate image ID: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def search_similar_images_by_vector(query_vector, limit=2):
    """Search for similar images by vector."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            response = artworks.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )
            return response.objects
    except Exception as e:
        logger.error(f"Error searching similar images by vector: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to search Weaviate: {str(e)}") from e


def read_all_artworks():
    """Read all artworks from Weaviate (for debugging)."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            logger.debug("Reading all artworks")
            for item in artworks.iterator():
                logger.debug(f"Artwork UUID: {item.uuid}, Properties: {item.properties}")
    except Exception as e:
        logger.error(f"Error reading all artworks: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to read from Weaviate: {str(e)}") from e


def get_image_by_weaviate_id(image_id):
    """Get an image by its Weaviate ID."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            logger.debug(f"Reading image by ID: {image_id}")
            data_object = artworks.query.fetch_object_by_id(image_id)
            logger.debug(f"Retrieved image data: {data_object}")
            return data_object
    except Exception as e:
        logger.error(f"Error getting image by Weaviate ID: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to fetch from Weaviate: {str(e)}") from e


def remove_by_weaviate_id(weaviate_id):
    """Remove an image by its Weaviate ID."""
    try:
        with get_weaviate_client() as weaviate_client:
            artworks = weaviate_client.collections.get("Artworks")
            logger.debug(f"Removing image by ID: {weaviate_id}")
            data_object = artworks.data.delete_by_id(weaviate_id)
            logger.debug(f"Removed image data: {data_object}")
            return data_object
    except Exception as e:
        logger.error(f"Error removing image by Weaviate ID: {e}", exc_info=True)
        raise WeaviateConnectionError(f"Failed to delete from Weaviate: {str(e)}") from e
