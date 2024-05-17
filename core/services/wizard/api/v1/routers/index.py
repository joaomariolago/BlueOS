from typing import Any, Iterable

from commonwealth.utils.streaming import timeout_streamer
from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi_versioning import version

from api.v1.models import Extension

# Global Kraken control instance
from kraken import kraken_instance

# Creates Root Kraken router
index_router_v1 = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# Endpoints

@index_router_v1.get("/", response_class=HTMLResponse, status_code=200)
@version(1, 0)
async def root() -> Any:
    html_content = """
    <html>
        <head>
            <title>Kraken</title>
        </head>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
