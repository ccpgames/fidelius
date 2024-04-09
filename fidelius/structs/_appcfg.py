__all__ = [
    'AppProps',
]
from ccptools.structs import *


@dataclasses.dataclass
class AppProps:
    """Application properties,  used to get or set specific variations of
    parameters/secrets.s

    :ivar app: The name of the application itself (module name or slug)
    :ivar group: The app's "group" (think "business domain" or "namespace").
                 The purpose of the "group" attribute is to categorize shared
                 parameters/secrets such that all apps in the same group, can
                 access all the shared (non-app specific) parameters/secrets of
                 that group.
    :ivar env: Deployment environment (e.g., "prod", "dev", "test").
    """
    app: str
    group: str
    env: str = 'default'
æ