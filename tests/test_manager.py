from pathlib import Path
import os
import pytest
import git
from dependency_manager import DependencyManagerAbstract

path_with_req = Path("tests/reqs_file_inside")
original_contents = """# file used to test dependency management
requests==2.31.0
black==23.7.*
mypy~=1.4
pylint>1
"""


@pytest.fixture()
def path_with_req_with_cleanup():
    """
    Yields the directory with the requirements and ensures it returns to its original state after.
    """
    path = "tests/reqs_file_inside"
    yield Path(path)
    repo = git.Git(os.getcwd())
    repo.execute(["git", "checkout", str(Path(os.getcwd()) / path)])


class TestManager:
    def test_must_define_parent_dir(self):
        class MyUnfinishedManager(DependencyManagerAbstract):
            pass

        with pytest.raises(TypeError):
            MyUnfinishedManager()

    def test_is_singleton(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        dm1 = DependencyManager()
        dm2 = DependencyManager()

        assert id(dm1) == id(dm2)

    def test_no_reqs_file_doesnt_error(self):
        dir_wo_reqs = Path("tests/no_reqs_files_inside")

        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return dir_wo_reqs

        manager = DependencyManager()
        assert manager.parent_directory == dir_wo_reqs
        assert manager.dependency_file is None
        assert not manager.dependencies

        DependencyManager().write()

    def test_find_deps(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        manager = DependencyManager()
        assert manager.dependency_file == path_with_req / "requirements.txt"
        assert len(manager.dependencies) == 4

    def test_add(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        manager = DependencyManager()
        assert manager.dependency_file == path_with_req / "requirements.txt"
        assert len(manager.dependencies) == 4

        DependencyManager().add(["my_pkg==1"])
        assert len(manager.dependencies) == 5
        my_pkg = next(reversed(manager.dependencies))
        assert str(my_pkg) == "my_pkg==1"

        DependencyManager().add(["my_pkg_no_ver"])
        assert len(manager.dependencies) == 6
        my_pkg = next(reversed(manager.dependencies))
        assert str(my_pkg) == "my_pkg_no_ver"

        # don't add already existing dep
        DependencyManager().add(["my_pkg_no_ver"])
        assert len(manager.dependencies) == 6

    def test_cant_handle_urls(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        manager = DependencyManager()

        assert len(manager.dependencies) == 4
        DependencyManager().add(["git+https://github.com/someproject/"])
        assert len(manager.dependencies) == 4

    def test_remove(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        manager = DependencyManager()
        assert manager.dependency_file == path_with_req / "requirements.txt"
        assert len(manager.dependencies) == 4

        first_dep = next(iter(manager.dependencies))
        manager.remove([str(first_dep)])
        assert len(manager.dependencies) == 3

        DependencyManager().remove(["git+https://github.com/someproject/"])
        assert len(manager.dependencies) == 3

        # Don't remove what isn't there
        DependencyManager().remove(["my_pkg==1"])
        assert len(manager.dependencies) == 3

    def test_dry_run(self, capsys):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        manager = DependencyManager()
        first_dep = next(iter(manager.dependencies))
        manager.remove([str(first_dep)])
        manager.write(dry_run=True)
        with open(manager.dependency_file, "r", encoding="utf-8") as dep_file:
            contents = dep_file.read()
        assert contents == original_contents
        expected = "black==23.7.*\nmypy~=1.4\npylint>1\n"
        captured = capsys.readouterr()
        assert captured.out == expected

    def test_write(self, path_with_req_with_cleanup):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req_with_cleanup

        manager = DependencyManager()
        first_dep = next(iter(manager.dependencies))
        manager.remove([str(first_dep)])
        manager.write()
        with open(manager.dependency_file, "r", encoding="utf-8") as dep_file:
            contents = dep_file.read()
        expected = "black==23.7.*\nmypy~=1.4\npylint>1"
        assert contents == expected
