from abc import ABC, abstractmethod


class AbstractCommand(ABC):
    @abstractmethod
    def execute(self):
        ...

    @abstractmethod
    def add_arguments(self):
        ...

    @abstractmethod
    def set_arguments(self):
        ...
