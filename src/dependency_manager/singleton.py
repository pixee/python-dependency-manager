class Singleton:
    """
    Base class that provides the Singleton pattern.

    We use the singleton pattern when we want to retain global state across
    all instances of the same class.
    """

    def __new__(cls, *args, **kwds):
        if (instance := cls.__dict__.get("__instance__")) is not None:
            return instance

        cls.__instance__ = instance = object.__new__(cls)
        instance.init(*args, **kwds)
        return instance

    def init(self, *args, **kwds):
        """
        Subclasses should override this method for initialization, not __init__.
        """
        pass

    @classmethod
    def clear_instance(cls):
        """Delete the singleton's current instance."""
        if (instance := cls.__dict__.get("__instance__")) is not None:
            del cls.__instance__
