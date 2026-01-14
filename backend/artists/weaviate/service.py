"""Business logic for Weaviate image operations."""
import base64
import requests
import socket
import ipaddress
import time
import logging
from urllib.parse import urlparse, urlunparse
from PIL import Image
from io import BytesIO
from weaviate.util import generate_uuid5

from .client import get_weaviate_client, PinnedDNSAdapter, _format_netloc
from .exceptions import WeaviateImageError, WeaviateSecurityError

logger = logging.getLogger(__name__)


def resize_image_if_needed(base64_string, max_size_mb=10):
    """Resize the image if it's too large."""
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
        raise WeaviateSecurityError(f"URL blocked by security policy: {url}")

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
            raise WeaviateImageError("Redirects are not allowed for image fetches")

        response.raise_for_status()

        # Enforce size limit via Content-Length when provided
        content_length = response.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
            except (ValueError, TypeError):
                size = None
            else:
                if size > max_bytes:
                    raise WeaviateImageError("Image exceeds 10MB size limit")

        # Stream download and enforce hard cap
        data = BytesIO()
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            downloaded += len(chunk)
            if downloaded > max_bytes:
                raise WeaviateImageError("Image exceeds 10MB size limit during download")
            data.write(chunk)

        image_bytes = data.getvalue()

        # Validate content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise WeaviateImageError(f"URL does not point to an image: {content_type}")

        # Validate the downloaded payload is a real image
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                img.verify()
        except Exception:
            raise WeaviateImageError("Downloaded content is not a valid image")

    # Convert to base64
    base64_string = base64.b64encode(image_bytes).decode()

    # Resize if needed
    return resize_image_if_needed(base64_string)


def check_object_exists(artworks, obj_uuid):
    """Check if an object exists in Weaviate."""
    import weaviate
    try:
        result = artworks.query.fetch_object_by_id(str(obj_uuid))
        return result is not None
    except (weaviate.exceptions.WeaviateException, Exception) as exc:
        logger.warning("Failed to check object %s: %s", obj_uuid, exc)
        return False


def remove_if_exists(artworks, obj_uuid):
    """Remove object if it exists in Weaviate."""
    try:
        if check_object_exists(artworks, obj_uuid):
            artworks.data.delete_by_id(str(obj_uuid))
            logger.debug(f"Removing already existing object with UUID: {obj_uuid}")
            time.sleep(0.5)  # Give Weaviate time to process the deletion
    except Exception as e:
        logger.error(f"Error removing existing object: {str(e)}")


def add_image_to_weaviete(artwork_psql_id, author_psql_id, arweave_image_url):
    """Add an image to Weaviate with retry logic."""
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
