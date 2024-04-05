__all__ = [
    'ParameterStoreAdmin',
]
from .paramstore import *
from fidelius.structs import *

import logging
log = logging.getLogger(__name__)


class ParameterStoreAdmin(ParameterStore):
    def __init__(self, app: str, group: str, env: str, owner: str, finance: str = 'COST', **extra_tags):
        super().__init__(app, group, env)
        self._tags = Tags(application=self._app, owner=owner, tier=env, finance=finance, **extra_tags)

    def set_env(self, env: str):
        self._env = env
        self._tags.tier = env

    def _set_parameter(self,
                       full_name: str,
                       value: str,
                       encrypted: bool = False,
                       overwrite: bool = False,
                       description: Optional[str] = None) -> Dict:
        kwargs = dict(Name=full_name,
                      Description=description or full_name,
                      Value=value,
                      Type='SecureString' if encrypted else 'String',
                      Overwrite=overwrite,
                      Tags=self._tags.to_aws_format(),
                      Tier='Standard')
        if encrypted:
            kwargs['KeyId'] = self._KEY_ID

        response = self._ssm.put_parameter(**kwargs)
        return response

    def create_param(self, name: str, value: str, description: Optional[str] = None):
        self._set_parameter(full_name=self._full_path(name),
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=False)

    def update_param(self, name: str, value: str, description: Optional[str] = None):
        if self.get(name=name, no_default=True):
            self._set_parameter(full_name=self._full_path(name),
                                value=value,
                                description=description,
                                overwrite=True,
                                encrypted=False)
        else:
            raise ValueError('that parameter does not exists yet, use create_param')

    def create_shared_param(self, name: str, folder: str, value: str, description: Optional[str] = None):
        self._set_parameter(full_name=self._full_path(name, folder),
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=False)

    def update_shared_param(self, name: str, folder: str, value: str, description: Optional[str] = None):
        self._set_parameter(full_name=self._full_path(name, folder),
                            value=value,
                            description=description,
                            overwrite=True,
                            encrypted=False)

    def create_secret(self, name: str, value: str, description: Optional[str] = None):
        self._set_parameter(full_name=self._full_path(name),
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=True)

    def update_secret(self, name: str, value: str, description: Optional[str] = None):
        if self.get(name=name, no_default=True):
            self._set_parameter(full_name=self._full_path(name),
                                value=value,
                                description=description,
                                overwrite=True,
                                encrypted=True)
        else:
            raise ValueError('that secret does not exists yet, use create_secret')

    def create_shared_secret(self, name: str, folder: str, value: str, description: Optional[str] = None):
        self._set_parameter(full_name=self._full_path(name, folder),
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=True)

    def update_shared_secret(self, name: str, folder: str, value: str, description: Optional[str] = None):
        self._set_parameter(full_name=self._full_path(name, folder),
                            value=value,
                            description=description,
                            overwrite=True,
                            encrypted=True)
