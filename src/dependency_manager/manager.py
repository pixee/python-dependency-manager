from abc import ABC, abstractmethod
from pathlib import Path
import pkg_resources
from .singleton import Singleton


class DependencyManagerAbstract(Singleton, ABC):
    def init(self):
        """One-time class initialization."""
        self.parent_directory = self.get_parent_dir()
        self.dependency_file = self._infer_dependency_files()
        self.dependencies = self._infer_dependencies()

    @abstractmethod
    def get_parent_dir(self) -> Path:
        """Must define which directory to use to start looking for the
        dependency file. Return a `Path` object, for example, `Path(os.getcwd())`
        """
        pass

    def add(self, dependencies: list[str]):
        """add any number of dependencies to the end of list of dependencies."""
        for dep_str in dependencies:
            try:
                dep = pkg_resources.Requirement(dep_str)
            except pkg_resources.extern.packaging.requirements.InvalidRequirement:
                continue
            self.dependencies.append(dep)

    def remove(self, dependencies: list[str]):
        """remove any number of dependencies from the list of dependencies"""
        pass
    def write(self):
        dependencies = [str(req) for req in self.dependencies]
        with open(self.dependency_file, "w", encoding="utf-8") as f:
            f.writelines("\n".join(dependencies))

    def _infer_dependency_files(self) -> Path:
        # For now for simplicity only return the first file
        return next(Path(self.parent_directory).rglob("requirements.txt"))

    def _infer_dependencies(self) -> list[pkg_resources.Requirement]:
        """
        Extract list of dependencies from requirements.txt file.
        Same order of requirements is maintained, no alphabetical sorting is done.
        """
        with open(self.dependency_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return list(pkg_resources.parse_requirements(lines))
