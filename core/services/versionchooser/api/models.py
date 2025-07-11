from typing import Optional
from pydantic import BaseModel


class Version(BaseModel):
    image: str
    tag: str


class DockerLoginInfo(BaseModel):
    username: str
    password: Optional[str] = None
    registry: Optional[str] = "https://index.docker.io/v1/"
    root: Optional[bool] = True


class VersionSetRequest(BaseModel):
    repository: str
    tag: str


class BootstrapVersionSetRequest(BaseModel):
    tag: str


class VersionDeleteRequest(BaseModel):
    repository: str
    tag: str


class VersionResponse(BaseModel):
    repository: str
    tag: str
    last_modified: str
    sha: str
    architecture: str


class AvailableVersionsResponse(BaseModel):
    remote: Optional[list[Version]] = None
    local: Optional[list[Version]] = None
    error: Optional[str] = None


class LocalVersionsResponse(BaseModel):
    local: Optional[list[Version]] = None
    error: Optional[str] = None


class DockerAccountsResponse(BaseModel):
    accounts: list[DockerLoginInfo]
