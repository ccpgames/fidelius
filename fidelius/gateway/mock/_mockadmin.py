__all__ = [
    'MockFideliusAdmin',
]

from fidelius.gateway._abstract import *
from fidelius.structs import *
from ._mockrepo import *

import logging
log = logging.getLogger(__name__)


class MockFideliusAdmin(_BaseFideliusAdminRepo, MockFideliusRepo):
    def __init__(self, app_props: FideliusAppProps, tags: Optional[FideliusTags] = None, **kwargs):
        """This mock version of the Fidelius Admin stores created and updated
        params in memory only (although the cache is a singleton so multiple
        instances of both admin and repo will be useing the same dict/data.

        Note that it does NOT extend the functionality of its non-Admin sibling,
        the MockFideliusRepo and thus does not return a base64 encoded version
        of every requested param/secret key name, but instead only uses its own
        internal in-memory cache, and thus, `get` will not return anything that
        hasn't been created first during that particular runtime.

        This is mainly intended for unit testing other packages and apps that
        use Fidelius.
        """
        log.debug('MockFideliusAdmin.__init__')
        super().__init__(app_props, tags, **kwargs)

    def _create(self, name: str, value: str, env: Optional[str] = None, folder: Optional[str] = None) -> (str, str):
        key = self.get_full_path(name, folder=folder, env=env)
        if key in self._cache:
            raise FideliusParameterAlreadyExists(f'parameter already exists: {key}')
        self._cache[key] = value
        return key, self.get_expression_string(name, folder=folder)

    def _update(self, name: str, value: str, env: Optional[str] = None, folder: Optional[str] = None) -> (str, str):
        key = self.get_full_path(name, folder=folder, env=env)
        if key not in self._cache:
            raise FideliusParameterNotFound(f'parameter not found: {key}')
        self._cache[key] = value
        return key, self.get_expression_string(name, folder=folder)

    def _delete(self, name: str, env: Optional[str] = None, folder: Optional[str] = None):
        key = self.get_full_path(name, folder=folder, env=env)
        if key not in self._cache:
            raise FideliusParameterNotFound(f'parameter not found: {key}')
        del self._cache[key]

    def create_param(self, name: str, value: str,
                     description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self._create(name, value=value, env=env)

    def update_param(self, name: str, value: str,
                     description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self._update(name, value=value, env=env)

    def delete_param(self, name: str, env: Optional[str] = None):
        self._delete(name, env=env)

    def create_shared_param(self, name: str, folder: str, value: str,
                            description: Optional[str] = None,
                            env: Optional[str] = None) -> (str, str):
        return self._create(name, value=value, env=env, folder=folder)

    def update_shared_param(self, name: str, folder: str, value: str,
                            description: Optional[str] = None,
                            env: Optional[str] = None) -> (str, str):
        return self._update(name, value=value, env=env, folder=folder)

    def delete_shared_param(self, name: str, folder: str, env: Optional[str] = None):
        self._delete(name, env=env, folder=folder)

    def create_secret(self, name: str, value: str,
                      description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self._create(name, value=value, env=env)

    def update_secret(self, name: str, value: str,
                      description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self._update(name, value=value, env=env)

    def delete_secret(self, name: str, env: Optional[str] = None):
        self._delete(name, env=env)

    def create_shared_secret(self, name: str, folder: str, value: str,
                             description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self._create(name, value=value, env=env, folder=folder)

    def update_shared_secret(self, name: str, folder: str, value: str,
                             description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self._update(name, value=value, env=env, folder=folder)

    def delete_shared_secret(self, name: str, folder: str, env: Optional[str] = None):
        self._delete(name, env=env, folder=folder)
