from os import path

from commonwealth.utils.apis import GenericErrorHandlingRoute
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI

# Routers
from api.v1.routers import extension_router_v1, index_router_v1
from api.v2.routers import (
    container_router_v2,
    extension_router_v2,
    index_router_v2,
    manifest_router_v2,
)

#
# Main API App
#

app = FastAPI(
    title="Kraken API",
    description="Kraken is the BlueOS service responsible for installing and managing extensions.",
)
app.router.route_class = GenericErrorHandlingRoute

# Adds routers to the app

# API v1
app.include_router(index_router_v1)
app.include_router(extension_router_v1)

# API v2
app.include_router(index_router_v2)
app.include_router(container_router_v2)
app.include_router(extension_router_v2)
app.include_router(manifest_router_v2)

# Adds API versioning
app = VersionedFastAPI(app, version="1.0.0", prefix_format="/v{major}.{minor}", enable_latest=True)

# Mount static files
app.mount("/static", StaticFiles(directory=path.join(path.dirname(__file__), "static")), name="static")
