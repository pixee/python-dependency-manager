# python-dependency-manager

## use cases:
- to infer a project's dependency file
  - at this time only requirements.txt supported
- to programmatically update the dependency file

## API:

The goal of dependency manager is to allow you to modify your project's stated dependencies - inside txt file - during the course
of your program. As such, we provide a DependencyManagerAbstract. The first step is to define your own manager:

```python
# app_manager.py
from dependency_manager import Dependency, DependencyManagerAbstract

class DependencyManager(DependencyManagerAbstract):
    def get_parent_dir(self):
        """Must return a string, but can use `os.getcwd()` or anything else"""
        return "/some/path"

```
Your `DependencyManager` is a now a  Singleton with one stated parent directory. This means that all the inference work done at initialization
will be cached for all except for calls to `DependencyManager()`. This work includes calling `get_parent_dir`, finding the dependency file within the parent_directory
you define, etc.

Once you've defined your manager, you can now use it:

```python
from dependency_manager import Dependency
from app_manager import DependencyManager

DependencyManager().add([Dependency(name="requests", version="2.8.8")])
...

DependencyManager().remove([Dependency(name="requests", version="*")])
...
DependencyManager().remove([Dependency(name="pylint", version="*")])

# Once you are ready to update the dependency file:
DependencyManager().write()
```


