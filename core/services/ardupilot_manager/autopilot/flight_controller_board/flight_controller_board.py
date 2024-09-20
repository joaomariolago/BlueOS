import abc

from autopilot.platform import AutopilotPlatform

class FlightControllerBoard(abc.ABC):
    id: str
    name: str
    #platform:




class FlightController(BaseModel):
    """Flight-controller board."""

    name: str
    manufacturer: Optional[str]
    platform: Platform
    path: Optional[str]
    flags: List[FlightControllerFlags] = []

    @property
    def type(self) -> PlatformType:
        return self.platform.type
