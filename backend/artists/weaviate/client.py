"""Weaviate client connection management."""
import weaviate
from contextlib import contextmanager
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urlunparse
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
    """Context manager for handling Weaviate client connections."""
    client = None
    try:
        client = weaviate.connect_to_local()
        yield client
    finally:
        if client is not None:
            client.close()
