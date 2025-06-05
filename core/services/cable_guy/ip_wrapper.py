import asyncio

from pyroute2 import IW, NDB, AsyncIPRoute

from commonwealth.utils.Singleton import Singleton


class IPWrapper(metaclass=Singleton):
    def __init__(self) -> None:
        self._ipr = AsyncIPRoute()
        self._iw = IW()
        self._ndb = NDB(log="on")
        self._lock = asyncio.Lock()

    @property
    def ipr(self) -> AsyncIPRoute:
        return self._ipr

    @property
    def iw(self) -> IW:
        return self._iw

    @property
    def ndb(self) -> NDB:
        return self._ndb

    @property
    def lock(self) -> asyncio.Lock:
        return self._lock


ip_wrapper = IPWrapper()
