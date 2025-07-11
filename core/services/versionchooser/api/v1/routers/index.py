import json
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi_versioning import versioned_api_route
from loguru import logger

from api.models import (
    AvailableVersionsResponse,
    BootstrapVersionSetRequest,
    DockerAccountsResponse,
    DockerLoginInfo,
    LocalVersionsResponse,
    VersionDeleteRequest,
    VersionResponse,
    VersionSetRequest,
)
from docker_login import get_docker_accounts, make_docker_login, make_docker_logout
from utils.chooser import STATIC_FOLDER, VersionChooser

index_router_v1 = APIRouter(
    tags=["index_v1"],
    route_class=versioned_api_route(1, 0),
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# Global instance of VersionChooser
version_chooser = None


def get_version_chooser() -> VersionChooser:
    global version_chooser
    if version_chooser is None:
        import aiodocker
        version_chooser = VersionChooser(aiodocker.Docker())
    return version_chooser


@index_router_v1.get("/", status_code=200)
async def index() -> FileResponse:
    """Serve index.html"""
    return FileResponse(str(STATIC_FOLDER.parent) + "/index.html", headers={"cache-control": "no-cache"})


@index_router_v1.get("/version/current", status_code=status.HTTP_200_OK, response_model=VersionResponse)
async def get_version(chooser: VersionChooser = Depends(get_version_chooser)) -> VersionResponse:
    """Return the current running version of BlueOS"""
    try:
        response = await chooser.get_version()
        if response.status == 200:
            data = await response.json()
            return VersionResponse(**data)
        else:
            raise HTTPException(status_code=response.status, detail=await response.text())
    except Exception as e:
        logger.error(f"Error getting version: {e}")
        raise HTTPException(status_code=500, detail="Unable to get current version")


@index_router_v1.post("/version/current", status_code=status.HTTP_200_OK)
async def set_version(
    request: VersionSetRequest, chooser: VersionChooser = Depends(get_version_chooser)
) -> StreamingResponse:
    """Sets the current version of BlueOS to a new tag"""
    try:
        response = await chooser.set_version(request.repository, request.tag)
        return StreamingResponse(
            response.body,
            media_type="application/x-www-form-urlencoded",
            headers=dict(response.headers),
        )
    except Exception as e:
        logger.error(f"Error setting version: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to set version: {e}")


@index_router_v1.delete("/version/delete", status_code=status.HTTP_200_OK)
async def delete_version(
    request: VersionDeleteRequest, chooser: VersionChooser = Depends(get_version_chooser)
) -> StreamingResponse:
    """Delete the selected version of BlueOS"""
    try:
        response = await chooser.delete_version(request.repository, request.tag)
        return StreamingResponse(
            response.body,
            media_type="application/x-www-form-urlencoded",
            headers=dict(response.headers),
        )
    except Exception as e:
        logger.error(f"Error deleting version: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to delete version: {e}")


@index_router_v1.get("/version/available/local", status_code=status.HTTP_200_OK, response_model=LocalVersionsResponse)
async def get_available_local_versions(chooser: VersionChooser = Depends(get_version_chooser)) -> LocalVersionsResponse:
    """Returns available local versions"""
    try:
        response = await chooser.get_available_local_versions()
        if response.status == 200:
            data = await response.json()
            return LocalVersionsResponse(**data)
        else:
            raise HTTPException(status_code=response.status, detail=await response.text())
    except Exception as e:
        logger.error(f"Error getting local versions: {e}")
        raise HTTPException(status_code=500, detail="Unable to get local versions")


@index_router_v1.get("/version/available/{repository}/{image}", status_code=status.HTTP_200_OK, response_model=AvailableVersionsResponse)
async def get_available_versions(
    repository: str, image: str, chooser: VersionChooser = Depends(get_version_chooser)
) -> AvailableVersionsResponse:
    """Returns available versions, both locally and in dockerhub"""
    try:
        response = await chooser.get_available_versions(f"{repository}/{image}")
        if response.status == 200:
            data = await response.json()
            return AvailableVersionsResponse(**data)
        else:
            raise HTTPException(status_code=response.status, detail=await response.text())
    except Exception as e:
        logger.error(f"Error getting available versions: {e}")
        raise HTTPException(status_code=500, detail="Unable to get available versions")


@index_router_v1.post("/version/pull/", status_code=status.HTTP_200_OK)
async def pull_version(
    request: VersionSetRequest, chooser: VersionChooser = Depends(get_version_chooser)
) -> StreamingResponse:
    """Pulls a version from dockerhub"""
    try:
        # Create a mock request object for the existing method
        class MockRequest:
            def __init__(self):
                pass

        response = await chooser.pull_version(MockRequest(), request.repository, request.tag)
        return StreamingResponse(
            response.body,
            media_type="application/x-www-form-urlencoded",
            headers=dict(response.headers),
        )
    except Exception as e:
        logger.error(f"Error pulling version: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to pull version: {e}")


@index_router_v1.post("/version/load/", status_code=status.HTTP_200_OK)
async def load_version(
    file: UploadFile = File(...), chooser: VersionChooser = Depends(get_version_chooser)
) -> JSONResponse:
    """Load a docker tar file"""
    try:
        data = await file.read()
        response = await chooser.load(data)
        if response.status == 200:
            return JSONResponse(content=await response.json())
        else:
            raise HTTPException(status_code=response.status, detail=await response.text())
    except Exception as e:
        logger.error(f"Error loading version: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to load version: {e}")


@index_router_v1.get("/bootstrap/current", status_code=status.HTTP_200_OK)
async def get_bootstrap_version(chooser: VersionChooser = Depends(get_version_chooser)) -> str:
    """Return the current running version of BlueOS-bootstrap"""
    try:
        return await chooser.get_bootstrap_version()
    except Exception as e:
        logger.error(f"Error getting bootstrap version: {e}")
        raise HTTPException(status_code=500, detail="Unable to get bootstrap version")


@index_router_v1.post("/bootstrap/current", status_code=status.HTTP_200_OK)
async def set_bootstrap_version(
    request: BootstrapVersionSetRequest, chooser: VersionChooser = Depends(get_version_chooser)
) -> StreamingResponse:
    """Sets the current version of BlueOS-bootstrap to a new tag"""
    try:
        response = await chooser.set_bootstrap_version(request.tag)
        return StreamingResponse(
            response.body,
            media_type="application/x-www-form-urlencoded",
            headers=dict(response.headers),
        )
    except Exception as e:
        logger.error(f"Error setting bootstrap version: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to set bootstrap version: {e}")


@index_router_v1.post("/version/restart", status_code=status.HTTP_200_OK)
async def restart(chooser: VersionChooser = Depends(get_version_chooser)) -> JSONResponse:
    """Restart the currently running docker container"""
    try:
        response = await chooser.restart()
        if response.status == 200:
            return JSONResponse(content=await response.json())
        else:
            raise HTTPException(status_code=response.status, detail=await response.text())
    except Exception as e:
        logger.error(f"Error restarting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart: {e}")


@index_router_v1.post("/docker/login/", status_code=status.HTTP_200_OK)
async def docker_login(request: DockerLoginInfo) -> JSONResponse:
    """Login Docker daemon to a registry"""
    try:
        make_docker_login(request)
        return JSONResponse(content={"message": "Successfully logged in"})
    except Exception as e:
        logger.error(f"Error logging in to Docker: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to login to Docker: {e}")


@index_router_v1.post("/docker/logout/", status_code=status.HTTP_200_OK)
async def docker_logout(request: DockerLoginInfo) -> JSONResponse:
    """Logout Docker daemon from a registry"""
    try:
        make_docker_logout(request)
        return JSONResponse(content={"message": "Successfully logged out"})
    except Exception as e:
        logger.error(f"Error logging out from Docker: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to logout from Docker: {e}")


@index_router_v1.get("/docker/accounts/", status_code=status.HTTP_200_OK, response_model=DockerAccountsResponse)
async def docker_accounts() -> DockerAccountsResponse:
    """Get the list of accounts logged in"""
    try:
        accounts_data = get_docker_accounts()
        return DockerAccountsResponse(accounts=[DockerLoginInfo(**account) for account in accounts_data])
    except Exception as e:
        logger.error(f"Error getting Docker accounts: {e}")
        raise HTTPException(status_code=500, detail="Unable to get Docker accounts")
