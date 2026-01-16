"""Weaviate integration module for artist registry.

This module provides functionality for:
- Client connection management
- Image processing and security validation
- Adding images to Weaviate
- Querying similar images and authors
"""

# Client connection
from .client import get_weaviate_client, PinnedDNSAdapter

# Business logic / Service layer
from .service import (
    add_image_to_weaviate,
    url_to_base64,
    is_safe_url,
    resize_image_if_needed,
)

# Query functions
from .queries import (
    search_similar_authors_ids_by_base64,
    search_similar_authors_ids_by_image_data,
    search_similar_authors_ids_by_image_url,
    search_similar_artwork_ids_by_image_url,
    search_similar_artwork_ids_by_image_data,
    search_similar_images_by_weaviate_image_id,
    search_similar_authors_by_weaviate_image_id,
    search_similar_images_by_vector,
    read_all_artworks,
    get_image_by_weaviate_id,
    remove_by_weaviate_id,
)

# Exceptions
from .exceptions import (
    WeaviateException,
    WeaviateConnectionError,
    WeaviateImageError,
    WeaviateSecurityError,
)

__all__ = [
    # Client
    'get_weaviate_client',
    'PinnedDNSAdapter',
    # Service
    'add_image_to_weaviate',
    'url_to_base64',
    'is_safe_url',
    'resize_image_if_needed',
    # Queries
    'search_similar_authors_ids_by_base64',
    'search_similar_authors_ids_by_image_data',
    'search_similar_authors_ids_by_image_url',
    'search_similar_artwork_ids_by_image_url',
    'search_similar_artwork_ids_by_image_data',
    'search_similar_images_by_weaviate_image_id',
    'search_similar_authors_by_weaviate_image_id',
    'search_similar_images_by_vector',
    'read_all_artworks',
    'get_image_by_weaviate_id',
    'remove_by_weaviate_id',
    # Exceptions
    'WeaviateException',
    'WeaviateConnectionError',
    'WeaviateImageError',
    'WeaviateSecurityError',
]
