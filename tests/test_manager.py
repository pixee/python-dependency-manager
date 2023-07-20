import os
from pathlib import Path
import pytest
from dependency_manager import DependencyManagerAbstract

path_with_req = Path("tests/reqs_file_inside")
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

        dm = DependencyManager()
        assert dm.parent_directory == dir_wo_reqs
        assert dm.dependency_file == None
        assert dm.dependencies == []

        DependencyManager().write()

    def test_find_deps(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        dm = DependencyManager()
        assert dm.dependency_file == path_with_req / "requirements.txt"
        assert len(dm.dependencies) == 4

    def test_add(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        dm = DependencyManager()
        assert dm.dependency_file == path_with_req / "requirements.txt"
        assert len(dm.dependencies) == 4

        DependencyManager().add(["my_pkg==1"])
        assert len(dm.dependencies) == 5
        my_pkg = dm.dependencies[-1]
        assert str(my_pkg) == "my_pkg==1"

        DependencyManager().add(["my_pkg_no_ver"])
        assert len(dm.dependencies) == 6
        my_pkg = dm.dependencies[-1]
        assert str(my_pkg) == "my_pkg_no_ver"

        # don't add already existing dep
        DependencyManager().add(["my_pkg_no_ver"])
        assert len(dm.dependencies) == 6

    def test_cant_handle_urls(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        dm = DependencyManager()

        assert len(dm.dependencies) == 4
        DependencyManager().add(["git+https://github.com/someproject/"])
        assert len(dm.dependencies) == 4
    def test_remove(self):
        class DependencyManager(DependencyManagerAbstract):
            def get_parent_dir(self):
                return path_with_req

        dm = DependencyManager()
        assert dm.dependency_file == path_with_req / "requirements.txt"
        assert len(dm.dependencies) == 4

        first_dep = dm.dependencies[0]
        dm.remove([str(first_dep)])
        assert len(dm.dependencies) == 3

        DependencyManager().remove(["git+https://github.com/someproject/"])
        assert len(dm.dependencies) == 3

        # Don't remove what isn't there
        DependencyManager().remove(["my_pkg==1"])
        assert len(dm.dependencies) == 3

    def test_write(self):
        # TODO:
        pass