__all__ = [
    'MockFideliusRepo',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *

import base64

import logging
log = logging.getLogger(__name__)


class MockFideliusRepo(_BaseFideliusRepo):
    def __init__(self, app_props: FideliusAppProps, **kwargs):
        """This mock variation of the FideliusRepo simply returns a base64
        encoded version of the full path of the requested parameter/secret.

        This is mainly intended for unit testing other packages and apps that
        use Fidelius.
        """
        log.debug('MockFideliusRepo.__init__')
        super().__init__(app_props, **kwargs)

    def get_app_param(self, name: str, env: Optional[str] = None) -> Optional[str]:
        return base64.encodebytes(self.get_full_path(name, env=env).encode('utf-8')).decode('utf-8').strip()

    def get_shared_param(self, name: str, folder: str, env: Optional[str] = None) -> Optional[str]:
        return base64.encodebytes(self.get_full_path(name, folder=folder, env=env).encode('utf-8')).decode('utf-8').strip()
