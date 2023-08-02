from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
import pkg_resources
from .singleton import Singleton
from functools import cached_property


class DependencyManagerAbstract(Singleton, ABC):
    def init(self):
        """One-time class initialization."""
        self.parent_directory = self.get_parent_dir()
        self.dependencies_changed = False
        self.dependency_file_changed = False

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
                self.dependencies.update({dep: None})
                self.dependencies_changed = True

    def remove(self, dependencies: list[str]):
        """remove any number of dependencies from the list of dependencies"""
        for dep_str in dependencies:
            try:
                dep = pkg_resources.Requirement(dep_str)
            except pkg_resources.extern.packaging.requirements.InvalidRequirement:
                continue

            if dep in self.dependencies:
                self.dependencies.pop(dep)
                self.dependencies_changed = True

    def write(self, dry_run=False):
        """
        Write the updated dependency files if any changes were made.
        If the dry_run flag is set, print it to stdout instead.
        """
        if not self.dependencies_changed:
            return

        dependencies = [str(req) for req in self.dependencies]
        if dry_run:
            print("\n".join(dependencies))
        else:
            self._write(dependencies)
        self.dependency_file_changed = True

    def _write(self, dependencies):
        with open(self.dependency_file, "w", encoding="utf-8") as f:
            f.writelines("\n".join(dependencies))

    @cached_property
    def dependency_file(self) -> Union[Path, None]:
        try:
            # For now for simplicity only return the first file
            return next(Path(self.parent_directory).rglob("requirements.txt"))
        except StopIteration:
            pass
        return None

    @cached_property
    def dependencies(self) -> dict[pkg_resources.Requirement, None]:
        """
        Extract list of dependencies from requirements.txt file.
        Same order of requirements is maintained, no alphabetical sorting is done.
        """
        if not self.dependency_file:
            return dict()
        with open(self.dependency_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return {req: None for req in pkg_resources.parse_requirements(lines)}
