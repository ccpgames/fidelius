__all__ = [
    'IFideliusRepo',
    'IFideliusAdminRepo',
]
import abc
from typing import *


class IFideliusRepo(abc.ABC):
    _APP_FULL_NAME = '/fidelius/{group}/{env}/apps/{app}/{name}'
    _SHARED_FULL_NAME = '/fidelius/{group}/{env}/shared/{folder}/{name}'

    @abc.abstractmethod
    def __init__(self, app: str, group: str, env: str, **kwargs):
        self._app = app
        self._group = group
        self._env = env

    @abc.abstractmethod
    def get(self, name: str, folder: Optional[str] = None, no_default: bool = False) -> Optional[str]:
        pass

    def full_path(self, name: str, folder: Optional[str] = None) -> str:
        if folder:
            return self._SHARED_FULL_NAME.format(group=self._group, folder=folder, env=self._env, name=name)
        else:
            return self._APP_FULL_NAME.format(group=self._group, app=self._app, env=self._env, name=name)

    def nameless_path(self, folder: Optional[str] = None) -> str:
        return self.full_path(name='', folder=folder)[:-1]


class IFideliusAdminRepo(IFideliusRepo):
    @abc.abstractmethod
    def __init__(self, app: str, group: str, env: str, owner: str, finance: str = 'COST', **extra_tags):
        pass

    @abc.abstractmethod
    def set_env(self, env: str):
        pass

    @abc.abstractmethod
    def create_param(self, name: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def update_param(self, name: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def create_shared_param(self, name: str, folder: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def update_shared_param(self, name: str, folder: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def create_secret(self, name: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def update_secret(self, name: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def create_shared_secret(self, name: str, folder: str, value: str, description: Optional[str] = None):
        pass

    @abc.abstractmethod
    def update_shared_secret(self, name: str, folder: str, value: str, description: Optional[str] = None):
        pass
