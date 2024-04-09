__all__ = [
    'ParameterStore',
]

from fidelius.structs import *
from fidelius.gateway.interface import *


import boto3
import os

import logging
log = logging.getLogger(__name__)


class ParameterStore(IFideliusRepo):
    _KEY_ID = os.environ.get('FIDELIUS_AWS_KEY_ARN', '')
    _DEFAULT_REGION_NAME = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1')

    def __init__(self, app: str, group: str, env: str):
        super().__init__(app, group, env)
        if not self._KEY_ID:
            raise RuntimeError('Fidelius requires the ARN for the KMS key to use to be in the FIDELIUS_AWS_KEY_ARN environment variable')

        self._app = app
        self._group = group
        self._env = env
        self._force_log_secrecy()
        self._ssm = boto3.client('ssm',
                                 region_name=os.environ.get('FIDELIUS_AWS_REGION_NAME', self._DEFAULT_REGION_NAME),
                                 aws_access_key_id=os.environ.get('FIDELIUS_AWS_ACCESS_KEY_ID', None),
                                 aws_secret_access_key=os.environ.get('FIDELIUS_AWS_SECRET_ACCESS_KEY', None))

        self._cache: Dict[str, str] = {}
        self._loaded: bool = False
        self._loaded_folders: Set[str] = set()
        self._default_store: Optional[ParameterStore] = None
        if self._env != 'default':
            self._default_store = ParameterStore(self._app, self._group, 'default')

    def _full_path(self, name: str, folder: Optional[str] = None) -> str:
        if folder:
            return self._SHARED_FULL_NAME.format(group=self._group, folder=folder, env=self._env, name=name)
        else:
            return self._APP_FULL_NAME.format(group=self._group, app=self._app, env=self._env, name=name)

    def _nameless_path(self, folder: Optional[str] = None) -> str:
        return self._full_path(name='', folder=folder)[:-1]

    def _force_log_secrecy(self):
        # We don't allow debug or less logging of botocore's HTTP requests cause
        # those logs have unencrypted passwords in them!
        botolog = logging.getLogger('botocore')
        if botolog.level < logging.INFO:
            botolog.setLevel(logging.INFO)

    def _load_all(self, folder: Optional[str] = None):
        self._force_log_secrecy()
        if folder:
            if folder in self._loaded_folders:
                return
        else:
            if self._loaded:
                return

        response = self._ssm.get_parameters_by_path(
            Path=self._nameless_path(folder),
            Recursive=True,
            WithDecryption=True
        )
        for p in response.get('Parameters', []):
            key = p.get('Name')
            if key:
                self._cache[key] = p.get('Value')

        if folder:
            self._loaded_folders.add(folder)
        else:
            self._loaded = True

    def get(self, name: str, folder: Optional[str] = None, no_default: bool = False) -> Optional[str]:
        self._load_all(folder)
        return self._cache.get(self._full_path(name, folder),
                               None if no_default else self._get_default(name, folder))

    def _get_default(self, name: str, folder: Optional[str] = None) -> Optional[str]:
        if self._default_store:
            return self._default_store.get(name, folder)
        return None
