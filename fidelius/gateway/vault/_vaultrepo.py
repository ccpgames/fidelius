__all__ = [
    'VaultKeyValRepo',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *
from ._client import *

import os

import logging
log = logging.getLogger(__name__)


class VaultKeyValRepo(_BaseFideliusRepo):
    def __init__(self, app_props: FideliusAppProps,
                 vault_url: Optional[str] = None,
                 vault_token: Optional[str] = None,

                 verify: Union[bool, str] = True,
                 timeout_sec: int = 30,
                 flush_cache_every_time: bool = False,
                 **kwargs):
        """Fidelius Admin Repo that uses Hashicorp's Vault and its Secrets Key/Value store as a backend

        VAULT_ADDR

        VAULT_TOKEN
        VAULT_CACERT
        VAULT_CAPATH
        VAULT_CLIENT_CERT
        VAULT_CLIENT_KEY

        :param app_props: The current application properties.

        ...

        :param flush_cache_every_time: Optional flat that'll flush the entire
                                       cache before every operation if set to
                                       True and is just intended for testing
                                       purposes.
        """
        super().__init__(app_props, **kwargs)
        self._flush_cache_every_time = flush_cache_every_time

        self._vault_url = vault_url or os.environ.get('FIDELIUS_VAULT_ADDR', '') or os.environ.get('VAULT_ADDR', '')
        if not self._vault_url:
            raise EnvironmentError('Fidelius VaultKeyValRepo requires the base API URL address for Vault when initialising or in the FIDELIUS_VAULT_ADDR or VAULT_ADDR environment variables')

        self._vault_token = vault_token or os.environ.get('FIDELIUS_VAULT_TOKEN', '') or os.environ.get('VAULT_TOKEN', '')
        if not self._vault_token:
            raise EnvironmentError('Fidelius VaultKeyValRepo requires a vault token to access Vault when initialising or in the FIDELIUS_VAULT_ADDR or VAULT_ADDR environment variables')

        self._verify = verify
        self._timeout_sec = timeout_sec

        self._gw = VaultGateway(url=self._vault_url, token=self._vault_token, verify=self._verify, timeout=self._timeout_sec)

    def _nameless_path(self, folder: Optional[str] = None, env: Optional[str] = None) -> str:
        return self.get_full_path(name='', folder=folder, env=env)[:-1]

    def get_app_param(self, name: str, env: Optional[str] = None) -> Optional[str]:
        return self._gw.get_secret_param(self._nameless_path(env=env), name)

    def get_shared_param(self, name: str, folder: str, env: Optional[str] = None) -> Optional[str]:
        return self._gw.get_secret_param(self._nameless_path(folder=folder, env=env), name)
