__all__ = [
    'MockFideliusRepo',
]

from fidelius.structs import *
from fidelius.gateway.interface import *

import json

import logging
log = logging.getLogger(__name__)


class MockFideliusRepo(IFideliusRepo):
    _APP_FULL_NAME = '/fidelius/{group}/{env}/apps/{app}/{name}'
    _SHARED_FULL_NAME = '/fidelius/{group}/{env}/shared/{folder}/{name}'

    def __init__(self, app: str, group: str, env: str, pre_seeded_cache: Optional[Union[dict, str]] = None, **kwargs):
        super().__init__(app, group, env)
        self._cache: Dict[str, str] = {}
        self._loaded: bool = False

        self._pre_seeded_cache = pre_seeded_cache

    def _load_all(self, folder: Optional[str] = None):
        if isinstance(self._pre_seeded_cache, dict):
            self._cache = self._pre_seeded_cache
        elif isinstance(self._pre_seeded_cache, str) and self._pre_seeded_cache.lower().endswith('.json'):
            with open(self._pre_seeded_cache, 'r') as fin:
                self._cache = json.load(fin)

    def get(self, name: str, folder: Optional[str] = None, no_default: bool = False) -> Optional[str]:
        pass
