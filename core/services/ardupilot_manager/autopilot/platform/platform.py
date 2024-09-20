import abc

class AutopilotPlatform(abc.ABC):
    def __init__(self, board: FlightController) -> None:
        self.board = board

    @abc.abstractmethod
    def is_running(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def restart(self) -> None:
        raise NotImplementedError
