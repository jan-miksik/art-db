from typing import Any, Optional

from rest_framework.response import Response


def standard_response(data: Any = None, error: Optional[str] = None, status: int = 200) -> Response:
    """
    Wrap responses in a consistent envelope.

    Args:
        data: Payload for successful responses.
        error: Error message for failures.
        status: HTTP status code.
    """
    return Response(
        {
            "success": error is None,
            "data": data if error is None else None,
            "error": error,
        },
        status=status,
    )


def success(data: Any = None, status: int = 200) -> Response:
    return standard_response(data=data, status=status)


def failure(message: str, status: int = 400) -> Response:
    return standard_response(data=None, error=message, status=status)
