from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
import pkg_resources
from .singleton import Singleton


class DependencyManagerAbstract(Singleton, ABC):
    def init(self, dry_run=False):
        """One-time class initialization."""
        self.parent_directory = self.get_parent_dir()
        self.dependency_file = self._infer_dependency_files()
        self.dependencies = self._infer_dependencies()
        self.dependencies_changed = False
        self.dependency_file_changed = False
        self.dry_run = dry_run

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

            if dep not in self.dependencies:
                self.dependencies.append(dep)
                self.dependencies_changed = True

    def remove(self, dependencies: list[str]):
        """remove any number of dependencies from the list of dependencies"""
        for dep_str in dependencies:
            try:
                dep = pkg_resources.Requirement(dep_str)
            except pkg_resources.extern.packaging.requirements.InvalidRequirement:
                continue

            if dep in self.dependencies:
                self.dependencies.remove(dep)
                self.dependencies_changed = True

    def write(self):
        """
        Write the updated dependency files if any changes were made.
        If the dry_run flag is set, print it to stdout instead.
        """
        if (
            not self.dependency_file
            or not self.dependencies
            or not self.dependencies_changed
        ):
            return

        dependencies = [str(req) for req in self.dependencies]
        if not self.dry_run:
            self._write(dependencies)
        else:
            print("\n".join(dependencies))
        self.dependency_file_changed = True

    def _write(self, dependencies):
        if not self.dry_run:
            with open(self.dependency_file, "w", encoding="utf-8") as f:
                f.writelines("\n".join(dependencies))

    def _infer_dependency_files(self) -> Union[Path, None]:
        try:
            # For now for simplicity only return the first file
            return next(Path(self.parent_directory).rglob("requirements.txt"))
        except StopIteration:
            pass
        return None

    def _infer_dependencies(self) -> list[pkg_resources.Requirement]:
        """
        Extract list of dependencies from requirements.txt file.
        Same order of requirements is maintained, no alphabetical sorting is done.
        """
        if not self.dependency_file:
            return []
        with open(self.dependency_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return list(pkg_resources.parse_requirements(lines))
