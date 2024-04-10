__all__ = [
    'AwsParamStoreRepo',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *


import boto3
import os

import logging
log = logging.getLogger(__name__)


class AwsParamStoreRepo(_BaseFideliusRepo):
    def __init__(self, app_props: FideliusAppProps,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None,
                 aws_key_arn: str = None,
                 aws_region_name: str = None,
                 **kwargs):
        super().__init__(app_props, **kwargs)

        self._aws_key_arn = aws_key_arn or os.environ.get('FIDELIUS_AWS_KEY_ARN', '')
        if not self._aws_key_arn:
            raise EnvironmentError('Fidelius AwsParamStoreRepo requires the ARN for the KMS key argument when initialising or in the FIDELIUS_AWS_KEY_ARN environment variable')

        self._region_name = aws_region_name or os.environ.get('FIDELIUS_AWS_REGION_NAME', None) or os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1')

        # TODO(thordurm@ccpgames.com>) 2024-04-09: Check for aws_access_key_id and/or aws_secret_access_key

        self._force_log_secrecy()
        self._ssm = boto3.client('ssm',
                                 region_name=self._region_name,
                                 aws_access_key_id=aws_access_key_id or os.environ.get('FIDELIUS_AWS_ACCESS_KEY_ID', None) or os.environ.get('AWS_ACCESS_KEY_ID', None),
                                 aws_secret_access_key=aws_secret_access_key or os.environ.get('FIDELIUS_AWS_SECRET_ACCESS_KEY', None) or os.environ.get('AWS_SECRET_ACCESS_KEY', None))

        self._cache: Dict[str, str] = {}
        self._loaded: bool = False
        self._loaded_folders: Set[str] = set()
        self._default_store: Optional[AwsParamStoreRepo] = None
        if self.app_props.env != 'default':
            self._default_store = AwsParamStoreRepo(app_props=FideliusAppProps(app=app_props.app, group=app_props.group, env='default'),
                                                    aws_access_key_id=aws_access_key_id,
                                                    aws_secret_access_key=aws_secret_access_key,
                                                    aws_key_arn=aws_key_arn,
                                                    aws_region_name=aws_region_name)

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
