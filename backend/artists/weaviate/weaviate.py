import weaviate
from weaviate.classes.query import MetadataQuery
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urlunparse
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


def _format_netloc(ip_str, port):
    """Return a netloc string for an IP (handles IPv6 bracket syntax)."""
    host = f"[{ip_str}]" if ":" in ip_str and not ip_str.startswith("[") else ip_str
    return f"{host}:{port}" if port else host


class PinnedDNSAdapter(HTTPAdapter):
    """
    HTTP adapter that pins a prevalidated IP while preserving TLS hostname checks.

    The adapter rewrites the request destination to the resolved IP but keeps
    SNI/hostname verification against the original hostname to avoid DNS rebinding
    between validation and request.
    """

    def __init__(self, resolved_ip, hostname, port=None, **kwargs):
        self.resolved_ip = resolved_ip
        self.hostname = hostname
        self.port = port
        super().__init__(**kwargs)

    def _pinned_url(self, url):
        parsed = urlparse(url)
        port = parsed.port or self.port
        netloc = _format_netloc(self.resolved_ip, port)
        return urlunparse(parsed._replace(netloc=netloc))

    def get_connection_with_tls_context(self, url, proxies=None, stream=False, timeout=None, verify=True, cert=None, **kwargs):
        return super().get_connection_with_tls_context(
            self._pinned_url(url), proxies=proxies, stream=stream, timeout=timeout, verify=verify, cert=cert, **kwargs
        )

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs.setdefault("assert_hostname", self.hostname)
        pool_kwargs.setdefault("server_hostname", self.hostname)
        return super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        proxy_kwargs.setdefault("assert_hostname", self.hostname)
        proxy_kwargs.setdefault("server_hostname", self.hostname)
        return super().proxy_manager_for(proxy, **proxy_kwargs)

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

    Returns a tuple of (hostname, resolved_ip, port) on success to enable DNS pinning.
    """
    try:
        parsed = urlparse(url)

        # Only allow https to avoid downgrade/MiTM on untrusted sources
        if parsed.scheme != 'https':
            logger.warning(f"SSRF protection: Blocked non-HTTPS scheme: {parsed.scheme}")
            return None

        hostname = parsed.hostname
        if not hostname:
            return None

        # Block localhost variations
        if hostname in ('localhost', '127.0.0.1', '0.0.0.0', '::1'):
            logger.warning(f"SSRF protection: Blocked localhost access: {hostname}")
            return None

        # Resolve hostname to all IPs (IPv4/IPv6) and check each
        try:
            addr_info = socket.getaddrinfo(hostname, parsed.port or 443)
        except (socket.gaierror, ValueError):
            logger.warning(f"SSRF protection: Blocked unresolvable host: {hostname}")
            return None

        resolved_ip = None

        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                logger.warning(f"SSRF protection: Invalid IP resolved for {hostname}: {ip_str}")
                return None

            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                logger.warning(f"SSRF protection: Blocked private/reserved IP: {ip}")
                return None

            # Keep the first validated IP to reuse for the request
            if resolved_ip is None:
                resolved_ip = ip_str

        if not resolved_ip:
            return None

        return hostname, resolved_ip, parsed.port or 443
    except Exception as e:
        logger.error(f"SSRF protection: URL validation error: {e}")
        return None


def url_to_base64(url, timeout=10):
    """
    Convert image URL to base64 with size checking.
    SECURITY: Includes SSRF protection and request timeout.
    """
    max_bytes = 10 * 1024 * 1024  # 10 MB hard cap

    # Validate URL for SSRF protection
    validation = is_safe_url(url)
    if not validation:
        raise ValueError(f"URL blocked by security policy: {url}")

    hostname, resolved_ip, port = validation
    parsed = urlparse(url)
    pinned_url = urlunparse(parsed._replace(netloc=_format_netloc(resolved_ip, port)))

    headers = {
        'User-Agent': 'ArtDB-ImageFetcher/1.0',
        'Accept': 'image/*',
        'Host': hostname,
    }

    # Make request with timeout and verify SSL using the pinned IP; disallow redirects
    with requests.Session() as session:
        adapter = PinnedDNSAdapter(resolved_ip, hostname, port)
        session.mount(f"{parsed.scheme}://{_format_netloc(resolved_ip, port)}", adapter)

        response = session.get(
            pinned_url,
            timeout=timeout,
            verify=True,
            headers=headers,
            allow_redirects=False,
            stream=True
        )

        if 300 <= response.status_code < 400:
            raise ValueError("Redirects are not allowed for image fetches")

        response.raise_for_status()

        # Enforce size limit via Content-Length when provided
        content_length = response.headers.get('content-length')
        if content_length:
            if content_length:
                try:
                    size = int(content_length)
                except (ValueError, TypeError):
                    size = None
                else:
                    if size > max_bytes:
                        raise ValueError("Image exceeds 10MB size limit")

        # Stream download and enforce hard cap
        data = BytesIO()
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            downloaded += len(chunk)
            if downloaded > max_bytes:
                raise ValueError("Image exceeds 10MB size limit during download")
            data.write(chunk)

        image_bytes = data.getvalue()

        # Validate content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ValueError(f"URL does not point to an image: {content_type}")

        # Validate the downloaded payload is a real image
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                img.verify()
        except Exception:
            raise ValueError("Downloaded content is not a valid image")

    # Convert to base64
    base64_string = base64.b64encode(image_bytes).decode()

    # Resize if needed
    return resize_image_if_needed(base64_string)




############################
# add image to weaviete
############################

def check_object_exists(artworks, obj_uuid):
    """Check if an object exists in Weaviate"""
    try:
        result = artworks.query.fetch_object_by_id(str(obj_uuid))
        return result is not None
    except (weaviate.exceptions.WeaviateException, Exception) as exc:
        logger.warning("Failed to check object %s: %s", obj_uuid, exc)
        return False

def remove_if_exists(artworks, obj_uuid):
    """Remove object if it exists in Weaviate"""
    try:
        if check_object_exists(artworks, obj_uuid):
            artworks.data.delete_by_id(str(obj_uuid))
            logger.debug(f"Removing already existing object with UUID: {obj_uuid}")
            time.sleep(0.5)  # Give Weaviate time to process the deletion
    except Exception as e:
        logger.error(f"Error removing existing object: {str(e)}")


def add_image_to_weaviate(artwork_psql_id, author_psql_id, arweave_image_url):
    """
    Add an image to Weaviate with retry logic.
    
    Args:
        artwork_psql_id: PostgreSQL ID of the artwork
        author_psql_id: PostgreSQL ID of the author/artist
        arweave_image_url: URL of the image on Arweave
        
    Returns:
        str: UUID of the created Weaviate object, or None if failed
        
    Example:
        >>> from artists.weaviate.weaviate import add_image_to_weaviate
        >>> uuid = add_image_to_weaviate('25', '1', 'https://arweave.net/0zYEjsrKFVa-qt9k9pO7W7j1M-Xyzj_y4MeEq5NY1Hk')
        >>> print(uuid)
    """
    logger.debug("Adding image to Weaviate")
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
                    logger.error(f"Error converting image to base64: {str(e)}")
                    return None

                data_properties = {
                    "artwork_psql_id": str(artwork_psql_id),
                    "author_psql_id": str(author_psql_id),
                    "image": base64_string
                }

                # Generate a deterministic ID, it will generate the same ID for the same data
                obj_uuid = generate_uuid5(data_properties)
                logger.debug(f"Adding image to Weaviate with UUID: {obj_uuid}")

                remove_if_exists(artworks, obj_uuid)

                uuid_str = artworks.data.insert(
                    properties=data_properties,
                    uuid=str(obj_uuid)
                )

                if check_object_exists(artworks, uuid_str):
                    logger.info(f"Artwork {artwork_psql_id} successfully added to Weaviate with ID {uuid_str}")
                    return uuid_str

                logger.warning(f"Failed to verify artwork {artwork_psql_id} in Weaviate")
                return None

            except Exception as e:
                logger.warning(f"Attempt {current_try + 1} failed: {str(e)}")
                current_try += 1
                if current_try < max_retries:
                    time.sleep(2)  # Wait before retrying

    logger.error(f"Failed to add artwork to Weaviate after {max_retries} attempts")
    return None


############################
# Search for similar authors
############################

def search_similar_authors_ids_by_base64(image_data_base64, limit=2):
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


def search_similar_authors_ids_by_image_data(image_data_bytes, limit=2):
    image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
    return search_similar_authors_ids_by_base64(image_data_base64, limit)


def search_similar_authors_ids_by_image_url(image_url, limit=2):
    image_data_base64 = url_to_base64(image_url)
    return search_similar_authors_ids_by_base64(image_data_base64, limit)


############################
# Search for similar images
############################

def search_similar_artwork_ids_by_image_url(image_url, limit=1):
    """
    Search for similar artwork IDs by image URL.
    
    Args:
        image_url: URL of the image to search for
        limit: Maximum number of results to return (default: 1)
        
    Returns:
        List of similar artwork objects
        
    Example:
        >>> from artists.weaviate.weaviate import search_similar_artwork_ids_by_image_url
        >>> results = search_similar_artwork_ids_by_image_url('https://arweave.net/dwUZ_GgXgjV86SAE8NH9cPwb4YovEpvqnZ2Xo1LwoGU')
        >>> print(results)
    """
    base64_string = url_to_base64(image_url)
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        response = artworks.query.near_image(
            near_image=base64_string,
            limit=limit
        )
        return response.objects


def search_similar_artwork_ids_by_image_data(image_data_bytes, limit=2):
    image_data_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        response = artworks.query.near_image(
            near_image=image_data_base64,
            limit=limit
        )
        return response.objects


def search_similar_images_by_weaviate_image_id(weaviate_image_id, limit=2):
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        response = artworks.query.near_object(
            near_object=weaviate_image_id,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )
        return response.objects


def search_similar_authors_by_weaviate_image_id(weaviate_image_id, limit=5):
    """
    Search for similar authors by Weaviate image ID.
    
    Returns unique authors (no duplicates) by iteratively filtering out
    already found author IDs.
    
    Args:
        weaviate_image_id: UUID of the Weaviate image object
        limit: Maximum number of unique authors to return (default: 5)
        
    Returns:
        List of artwork objects with unique author_psql_id values
        
    Example:
        >>> import os
        >>> import django
        >>> django.setup()
        >>> from artists.weaviate.weaviate import search_similar_authors_by_weaviate_image_id
        >>> results = search_similar_authors_by_weaviate_image_id('2b265d11-20f9-55ba-9a2a-fbcdf89bdb07')
        >>> print(results)
    """
    with get_weaviate_client() as weaviate_client:
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
                filters = new_filter if filters is None else filters & new_filter

        return responses


def search_similar_images_by_vector(query_vector, limit=2):
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        response = artworks.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )
        return response.objects


def read_all_artworks():
    """
    Read and log all artworks from Weaviate.
    
    This function iterates through all artworks in the Weaviate collection
    and logs their UUID and properties. Useful for debugging and inspection.
    
    Example:
        >>> import os
        >>> import django
        >>> django.setup()
        >>> from artists.weaviate.weaviate import read_all_artworks
        >>> read_all_artworks()
    """
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        logger.debug("Reading all artworks")
        for item in artworks.iterator():
            logger.debug(f"Artwork UUID: {item.uuid}, Properties: {item.properties}")


def get_image_by_weaviate_id(image_id):
    """
    Retrieve an image object from Weaviate by its ID.
    
    Args:
        image_id: UUID of the Weaviate image object
        
    Returns:
        The Weaviate data object containing the image and metadata
        
    Example:
        >>> import os
        >>> import django
        >>> django.setup()
        >>> from artists.weaviate.weaviate import get_image_by_weaviate_id
        >>> image_obj = get_image_by_weaviate_id('498defaf-5b7e-52e4-ac96-ae2b5dcc278b')
        >>> print(image_obj)
    """
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        logger.debug(f"Reading image by ID: {image_id}")
        data_object = artworks.query.fetch_object_by_id(image_id)
        logger.debug(f"Retrieved image data: {data_object}")
        return data_object


def remove_by_weaviate_id(weaviate_id):
    """
    Remove an image object from Weaviate by its ID.
    
    Args:
        weaviate_id: UUID of the Weaviate object to remove
        
    Returns:
        The result of the deletion operation
        
    Example:
        >>> import os
        >>> import django
        >>> django.setup()
        >>> from artists.weaviate.weaviate import remove_by_weaviate_id
        >>> result = remove_by_weaviate_id('e3a39360-aacc-5214-829a-4f23b8a8c3eb')
        >>> print(result)
    """
    with get_weaviate_client() as weaviate_client:
        artworks = weaviate_client.collections.get("Artworks")
        logger.debug(f"Removing image by ID: {weaviate_id}")
        data_object = artworks.data.delete_by_id(weaviate_id)
        logger.debug(f"Removed image data: {data_object}")
        return data_object
