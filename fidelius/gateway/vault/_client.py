__all__ = [
    'VaultGateway',
]
from fidelius.structs import *
from ._structs import *
import hvac


import logging
log = logging.getLogger(__file__)


class VaultGateway:
    def __init__(self, url: str, token: str, verify: bool = True, timeout: int = 30, namespace: Optional[str] = None):
        self._client = hvac.Client(url=url, token=token, verify=verify, timeout=timeout, namespace=namespace)
        self._keyvals: Dict[str, Dict[str, str]] = {}  # self._keyvals[path][key] = val

    def flush_cache(self):
        self._keyvals = {}

    def _read_secret(self, path: str) -> VaultResponse:
        res_dict = self._client.secrets.kv.read_secret(path=path)
        return VaultResponse.from_dict(res_dict)

    def _load_path(self, path: str):
        if path not in self._keyvals:
            self._keyvals[path] = {}
            res = self._read_secret(path)
            if res.data and isinstance(res.data.data, dict):
                self._keyvals[path] = res.data.data
            else:
                log.error(f'The data for requested path was not a dict or doesnt exist! {path=}, {res=}')

    def get_secret_param(self, path: str, key: str) -> Optional[str]:
        self._load_path(path)
        return self._keyvals[path].get(key, None)

    def _force_path_update(self, path: str):
        # First, clear this path from the cache!
        if path in self._keyvals:
            del self._keyvals[path]
        # Then, load the path so we're up to date!
        self._load_path(path)

    def create_secret_param(self, path: str, key: str, value: str):
        self._force_path_update(path)
        old_data = self._keyvals[path]
        if key in old_data:
            raise FideliusParameterAlreadyExists(f'parameter already exists: {path}/{key}')
        old_data[key] = value
        self._client.secrets.kv.create_or_update_secret(path=path, secret=old_data)
        self._force_path_update(path)

    def set_metadata(self, path: str, metadata: Dict[str, str]):
        self._client.secrets.kv.update_metadata(path=path, custom_metadata=metadata)

    def update_secret_param(self, path: str, key: str, value: str):
        self._force_path_update(path)
        old_data = self._keyvals[path]
        if key not in old_data:
            raise FideliusParameterNotFound(f'parameter not found: {path}/{key}')
        old_data[key] = value
        self._client.secrets.kv.create_or_update_secret(path=path, secret=old_data)
        self._force_path_update(path)

    def delete_secret_param(self, path: str, key: str):
        self._force_path_update(path)
        old_data = self._keyvals[path]
        if key not in old_data:
            raise FideliusParameterNotFound(f'parameter not found: {path}/{key}')
        del old_data[key]
        self._client.secrets.kv.create_or_update_secret(path=path, secret=old_data)
        self._force_path_update(path)
