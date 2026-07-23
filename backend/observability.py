from __future__ import annotations

import json
import logging
import os
import time
from uuid import uuid4

from fastapi import Request
from starlette.responses import Response


logger = logging.getLogger(
    "stackers.request",
)

logger.setLevel(
    os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper(),
)

if not logger.handlers:
    handler = logging.StreamHandler()

    handler.setFormatter(
        logging.Formatter(
            "%(message)s",
        ),
    )

    logger.addHandler(handler)

logger.propagate = False


def _request_id(
    request: Request,
) -> str:
    supplied_request_id = (
        request.headers.get(
            "X-Request-ID",
        )
    )

    if supplied_request_id:
        return supplied_request_id[:128]

    return str(uuid4())


def _duration_ms(
    started: float,
) -> float:
    return round(
        (
            time.perf_counter()
            - started
        )
        * 1000,
        2,
    )


async def request_observability_middleware(
    request: Request,
    call_next,
) -> Response:
    request_id = _request_id(
        request,
    )

    request.state.request_id = (
        request_id
    )

    started = time.perf_counter()

    client_ip = (
        request.client.host
        if request.client
        else None
    )

    try:
        response = await call_next(
            request,
        )
    except Exception:
        logger.exception(
            json.dumps(
                {
                    "event":
                        "request_failed",

                    "request_id":
                        request_id,

                    "method":
                        request.method,

                    "path":
                        request.url.path,

                    "client_ip":
                        client_ip,

                    "duration_ms":
                        _duration_ms(
                            started,
                        ),
                },
                separators=(",", ":"),
            ),
        )

        raise

    response.headers[
        "X-Request-ID"
    ] = request_id

    logger.info(
        json.dumps(
            {
                "event":
                    "request_completed",

                "request_id":
                    request_id,

                "method":
                    request.method,

                "path":
                    request.url.path,

                "status_code":
                    response.status_code,

                "client_ip":
                    client_ip,

                "duration_ms":
                    _duration_ms(
                        started,
                    ),
            },
            separators=(",", ":"),
        ),
    )

    return response
