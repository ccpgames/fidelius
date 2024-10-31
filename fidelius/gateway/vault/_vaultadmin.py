__all__ = [
    'VaultKeyValAdmin',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *
from ._vaultrepo import *

import logging
log = logging.getLogger(__name__)


class VaultKeyValAdmin(_BaseFideliusAdminRepo, VaultKeyValRepo):
    def __init__(self, app_props: FideliusAppProps, tags: Optional[FideliusTags] = None, **kwargs):
        log.debug('VaultKeyValAdmin.__init__')
        super().__init__(app_props, tags, **kwargs)

    def create_param(self, name: str, value: str,
                     description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        self._gw.create_secret_param(path=self._nameless_path(env=env), key=name, value=value)
        self._gw.set_metadata(path=self._nameless_path(env=env), metadata=self.tags.to_dict())
        return self.get_full_path(name, env=env), self.get_expression_string(name)

    def update_param(self, name: str, value: str,
                     description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        self._gw.update_secret_param(path=self._nameless_path(env=env), key=name, value=value)
        return self.get_full_path(name, env=env), self.get_expression_string(name)

    def delete_param(self, name: str, env: Optional[str] = None):
        self._gw.delete_secret_param(path=self._nameless_path(env=env), key=name)

    def create_shared_param(self, name: str, folder: str, value: str,
                            description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        self._gw.create_secret_param(path=self._nameless_path(folder=folder, env=env), key=name, value=value)
        self._gw.set_metadata(path=self._nameless_path(folder=folder, env=env), metadata=self.tags.to_dict())
        return self.get_full_path(name, folder=folder, env=env), self.get_expression_string(name, folder=folder)

    def update_shared_param(self, name: str, folder: str, value: str,
                            description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        self._gw.update_secret_param(path=self._nameless_path(folder=folder, env=env), key=name, value=value)
        return self.get_full_path(name, folder=folder, env=env), self.get_expression_string(name, folder=folder)

    def delete_shared_param(self, name: str, folder: str, env: Optional[str] = None):
        self._gw.delete_secret_param(path=self._nameless_path(env=env, folder=folder), key=name)

    def create_secret(self, name: str, value: str,
                      description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self.create_param(name=name, value=value, description=description, env=env)

    def update_secret(self, name: str, value: str,
                      description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self.update_param(name=name, value=value, description=description, env=env)

    def delete_secret(self, name: str, env: Optional[str] = None):
        self.delete_param(name=name, env=env)

    def create_shared_secret(self, name: str, folder: str, value: str,
                             description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self.create_shared_param(name=name, folder=folder, value=value, description=description, env=env)

    def update_shared_secret(self, name: str, folder: str, value: str,
                             description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        return self.update_shared_param(name=name, folder=folder, value=value, description=description, env=env)

    def delete_shared_secret(self, name: str, folder: str, env: Optional[str] = None):
        self.delete_shared_param(name=name, folder=folder, env=env)
