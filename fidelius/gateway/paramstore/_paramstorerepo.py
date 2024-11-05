__all__ = [
    'AwsParamStoreRepo',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *

import os

import logging
log = logging.getLogger(__name__)

try:
    import boto3
except ImportError:
    log.error('You are trying to use the AwsParamStoreRepo without boto3 installed.')
    log.error('Please amend your pip install to `fidelius[aws]` to include boto3 dependencies.')
    raise


class AwsParamStoreRepo(_BaseFideliusRepo):
    def __init__(self, app_props: FideliusAppProps,
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_key_arn: Optional[str] = None,
                 aws_region_name: Optional[str] = None,
                 aws_endpoint_url: Optional[str] = None,
                 aws_profile_name: Optional[str] = None,
                 flush_cache_every_time: bool = False,
                 **kwargs):
        """Fidelius Admin Repo that uses AWS' Simple Systems Manager's Parameter Store as a back end.

        :param app_props: The current application properties.
        :param aws_access_key_id: Optional AWS_ACCESS_KEY_ID which is otherwise
                                  pulled from the FIDELIUS_AWS_ACCESS_KEY_ID or
                                  AWS_ACCESS_KEY_ID environment variables.
        :param aws_secret_access_key: Optional AWS_SECRET_ACCESS_KEY which is otherwise
                                      pulled from the FIDELIUS_AWS_SECRET_ACCESS_KEY or
                                      AWS_SECRET_ACCESS_KEY environment variables.
        :param aws_key_arn: Optional ARN to an AWS KMS encryption key that'll be
                            used to encrypt secret parameters. If not provided
                            it'll be extracted from the FIDELIUS_AWS_KEY_ARN
                            environment variable and if that is missing as well,
                            an EnvironmentError is raised.
        :param aws_region_name: Optional AWS region name, which is otherwise
                                extracted from the FIDELIUS_AWS_REGION_NAME or
                                AWS_DEFAULT_REGION environment variables or just
                                set to `eu-west-1` by default is completely
                                missing.
        :param aws_endpoint_url: Optional custom AWS endpoint URL intended for
                                 testing and development, e.g. by spinning up a
                                 LocalStack container and pointing to that
                                 instead of a live AWS environment.
        :param aws_profile_name: ....add this @TODO
        :param flush_cache_every_time: Optional flat that'll flush the entire
                                       cache before every operation if set to
                                       True and is just intended for testing
                                       purposes.
        """
        super().__init__(app_props, **kwargs)
        self._flush_cache_every_time = flush_cache_every_time

        self._aws_key_arn = aws_key_arn or os.environ.get('FIDELIUS_AWS_KEY_ARN', '')
        if not self._aws_key_arn:
            raise EnvironmentError('Fidelius AwsParamStoreRepo requires the ARN for the KMS key argument when initialising or in the FIDELIUS_AWS_KEY_ARN environment variable')

        self._region_name = aws_region_name or os.environ.get('FIDELIUS_AWS_REGION_NAME', None)

        self._aws_endpoint_url = aws_endpoint_url or os.environ.get('FIDELIUS_AWS_ENDPOINT_URL', None)
        self._aws_profile_name = aws_profile_name or os.environ.get('FIDELIUS_AWS_PROFILE', None)

        self._force_log_secrecy()
        self._session = boto3.Session(profile_name=self._aws_profile_name,
                                      region_name=self._region_name,
                                      aws_access_key_id=aws_access_key_id or os.environ.get(
                                          'FIDELIUS_AWS_ACCESS_KEY_ID', None),
                                      aws_secret_access_key=aws_secret_access_key or os.environ.get(
                                          'FIDELIUS_AWS_SECRET_ACCESS_KEY', None))
        self._ssm = self._session.client('ssm',
                                         endpoint_url=self._aws_endpoint_url or None)

        self._cache: Dict[str, str] = {}
        self._loaded_paths: Set[str] = set()

    def _nameless_path(self, folder: Optional[str] = None, env: Optional[str] = None) -> str:
        return self.get_full_path(name='', folder=folder, env=env)[:-1]

    @staticmethod
    def _force_log_secrecy():
        # We don't allow debug or less logging of botocore's HTTP requests cause
        # those logs have unencrypted passwords in them!
        botolog = logging.getLogger('botocore')
        if botolog.level < logging.INFO:
            botolog.setLevel(logging.INFO)

    def _load_path(self, folder: Optional[str] = None, env: Optional[str] = None):
        log.debug('AwsParamStoreRepo._load_path(folder=%s, env=%s)', folder, env)
        self._force_log_secrecy()

        # This is stuff for unit-testing only!
        if self._flush_cache_every_time:
            self._loaded_paths = set()
            self._cache = {}

        path = self._nameless_path(folder, env)
        if path in self._loaded_paths:
            return

        response = self._ssm.get_parameters_by_path(
            Path=path,
            Recursive=True,
            WithDecryption=True
        )

        for p in response.get('Parameters', []):
            key = p.get('Name')
            if key:
                self._cache[key] = p.get('Value')

        self._loaded_paths.add(path)

    def get_app_param(self, name: str, env: Optional[str] = None) -> Optional[str]:
        self._load_path(env=env)
        return self._cache.get(self.get_full_path(name, env=env), None)

    def get_shared_param(self, name: str, folder: str, env: Optional[str] = None) -> Optional[str]:
        self._load_path(folder=folder, env=env)
        return self._cache.get(self.get_full_path(name, folder, env=env), None)
