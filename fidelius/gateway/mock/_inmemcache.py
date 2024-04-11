__all__ = [
    '_SingletonDict',
]

from ccptools.structs import *


class _SingletonDict(dict, metaclass=Singleton):
    """Simple Singleton dict :)

    It's point is simply to act as a shared centralized store for the mock
    stuff, mimicking how multiple instances of Fidelius Repos and/or Admin
    Repos would nevertheless fetch data from the same source.

    This is just to "mock" the shared parameter/secret stuff.

    ...sneaky, right?
    """
    pass
