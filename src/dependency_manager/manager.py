from abc import ABC, abstractmethod
from collections import namedtuple
from .singleton import Singleton

Dependency = namedtuple("Dependency", ["name", "version"])

class DependencyManagerAbstract(Singleton, ABC):
    def init(self):
        """One-time class initialization."""
        self.parent_directory = self.get_parent_dir()
        self.dependencies = self._infer_dependencies()

    @abstractmethod
    def get_parent_dir(self) -> str:
        """Must define which directory to use to start looking for the
        dependency file. Can return a string or something more complex.
        """
        pass

    def add(self, dependencies: list[Dependency]):
        pass
    def remove(self, dependencies: list[Dependency]):
        pass
    def write(self):
        pass

    def _infer_dependencies(self) -> list:
        # breakpoint()
        self.parent_directory
        # glob for very first requirements.txt file found