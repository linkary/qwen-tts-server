"""
Development-only helper endpoints.

Everything in here hands out information that must not leave a developer's machine.
app.main registers this router only when settings.expose_api_key is true and
settings.env != "production"; the in-handler check below is a second, independent gate
so the route stays inert even if a future refactor registers it unconditionally.
"""
import ipaddress
import logging
from typing import Optional
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, status

from app.config import settings
from app.models.schemas import DevApiKeyResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])


def _mask(secret: str) -> str:
    """First two and last two characters, mirroring the masking run.sh prints at startup."""
    return "****" if len(secret) <= 4 else f"{secret[:2]}****{secret[-2:]}"


def _is_loopback_host(host: str) -> bool:
    """True for localhost, *.localhost (RFC 6761), 127.0.0.0/8, ::1 and ::ffff:127.x."""
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    # ipaddress does not treat IPv4-mapped addresses as loopback, so unwrap first:
    # ip_address("::ffff:127.0.0.1").is_loopback is False.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_loopback


def _is_local_origin(origin: Optional[str]) -> bool:
    """
    True when the request carries no Origin header (curl, TestClient, other server-side
    clients) or was made by a page served from a loopback address.

    CORS_ORIGINS defaults to "*", so without this check any website the developer happens
    to visit could read this response cross-origin. A browser always sets Origin on a
    cross-origin fetch and a page cannot forge it, which is what makes this effective --
    and unlike a check on the peer IP it is unaffected by Docker's bridge NAT.
    """
    if origin is None:
        return True
    return _is_loopback_host(urlsplit(origin).hostname or "")


@router.get("/api-key", response_model=DevApiKeyResponse)
async def get_dev_api_key(request: Request) -> DevApiKeyResponse:
    """
    Return the API key this server accepts, so the bundled demo UI can fill it in.

    Development convenience only. Requires EXPOSE_API_KEY=true and ENV != production.
    """
    if not settings.expose_api_key or settings.env == "production":
        # 404 rather than 403: a caller must not learn that this feature exists at all.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    origin = request.headers.get("origin")
    if not _is_local_origin(origin):
        logger.warning("Refused API key request from non-local origin %r", origin)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Logged as an audit trail only. It deliberately gates nothing: with published
    # container ports the peer is the Docker bridge gateway, not loopback.
    peer = request.client.host if request.client else "unknown"
    keys = settings.get_api_keys_list()

    if not keys:
        logger.warning("API key requested by %s but no API_KEYS are configured", peer)
        return DevApiKeyResponse(auth_required=False, api_key=None, key_count=0)

    logger.warning(
        "Handing out API key %s to %s (origin=%s)",
        _mask(keys[0]),
        peer,
        origin or "none",
    )
    return DevApiKeyResponse(auth_required=True, api_key=keys[0], key_count=len(keys))
