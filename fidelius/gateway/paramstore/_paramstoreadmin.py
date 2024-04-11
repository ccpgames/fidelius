__all__ = [
    'AwsParameterStoreAdmin',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *
from ._paramstorerepo import *

import logging
log = logging.getLogger(__name__)


class AwsParameterStoreAdmin(_BaseFideliusAdminRepo, AwsParamStoreRepo):
    def __init__(self, app_props: FideliusAppProps, tags: Optional[FideliusTags] = None, **kwargs):
        log.debug('AwsParameterStoreAdmin.__init__')
        super().__init__(app_props, tags, **kwargs)

    def create_param(self, name: str, value: str,
                     description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, env=env)
        res = self._set_parameter(full_name=path,
                                  value=value,
                                  description=description,
                                  overwrite=False,
                                  encrypted=False)
        return path, self.get_expression_string(name)

    def update_param(self, name: str, value: str,
                     description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, env=env)
        if self.get_app_param(name, env=env) is None:
            raise FideliusParameterNotFound(f'parameter not found: {path}')

        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=True,
                            encrypted=False)
        return path, self.get_expression_string(name)

    def delete_param(self, name: str, env: Optional[str] = None):
        self._delete_parameter(full_name=self.get_full_path(name, env=env))

    def create_shared_param(self, name: str, folder: str, value: str,
                            description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, folder=folder, env=env)
        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=False)
        return path, self.get_expression_string(name, folder=folder)

    def update_shared_param(self, name: str, folder: str, value: str,
                            description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, folder=folder, env=env)
        if self.get_shared_param(name, folder=folder, env=env) is None:
            raise FideliusParameterNotFound(f'parameter not found: {path}')

        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=True,
                            encrypted=False)
        return path, self.get_expression_string(name, folder=folder)

    def delete_shared_param(self, name: str, folder: str, env: Optional[str] = None):
        self._delete_parameter(full_name=self.get_full_path(name, folder=folder, env=env))

    def create_secret(self, name: str, value: str,
                      description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, env=env)
        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=True)
        return path, self.get_expression_string(name)

    def update_secret(self, name: str, value: str,
                      description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, env=env)
        if self.get_app_param(name, env=env) is None:
            raise FideliusParameterNotFound(f'parameter not found: {path}')

        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=True,
                            encrypted=True)
        return path, self.get_expression_string(name)

    def delete_secret(self, name: str, env: Optional[str] = None):
        self._delete_parameter(full_name=self.get_full_path(name, env=env))

    def create_shared_secret(self, name: str, folder: str, value: str,
                             description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, folder=folder, env=env)
        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=False,
                            encrypted=True)
        return path, self.get_expression_string(name, folder=folder)

    def update_shared_secret(self, name: str, folder: str, value: str,
                             description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        path = self.get_full_path(name, folder=folder, env=env)
        if self.get_shared_param(name, folder=folder, env=env) is None:
            raise FideliusParameterNotFound(f'parameter not found: {path}')

        self._set_parameter(full_name=path,
                            value=value,
                            description=description,
                            overwrite=True,
                            encrypted=True)
        return path, self.get_expression_string(name, folder=folder)

    def delete_shared_secret(self, name: str, folder: str, env: Optional[str] = None):
        self._delete_parameter(full_name=self.get_full_path(name, folder=folder, env=env))

    def _tags_to_aws_format(self) -> Optional[List[Dict[str, str]]]:
        if self.tags:
            return [{'Key': k, 'Value': v} for k, v in self.tags.to_dict().items()]
        return None

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
                      Tier='Standard')
        if not overwrite:
            tags = self._tags_to_aws_format()
            if tags:
                kwargs['Tags'] = tags

        if encrypted:
            kwargs['KeyId'] = self._aws_key_arn

        try:
            response = self._ssm.put_parameter(**kwargs)
            return response
        except self._ssm.exceptions.ParameterAlreadyExists:
            raise FideliusParameterAlreadyExists(f'parameter already exists: {full_name}')

        except self._ssm.exceptions.ParameterNotFound:
            raise FideliusParameterNotFound(f'parameter not found: {full_name}')

    def _delete_parameter(self, full_name: str) -> Dict:
        try:
            response = self._ssm.delete_parameter(Name=full_name)
            return response
        except self._ssm.exceptions.ParameterNotFound:
            raise FideliusParameterNotFound(f'parameter not found: {full_name}')
