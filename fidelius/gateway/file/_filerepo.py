__all__ = [
    'MockFideliusRepo',
]

from fidelius.structs import *
from fidelius.gateway._abstract import *

import json

import logging
log = logging.getLogger(__name__)


class MockFideliusRepo(_BaseFideliusRepo):
    def __init__(self, app_props: FideliusAppProps, pre_seeded_cache: Optional[Union[dict, str]] = None, **kwargs):
        super().__init__(app_props, **kwargs)
        self._cache: Dict[str, str] = {}
        self._loaded: bool = False

        self._pre_seeded_cache = pre_seeded_cache

    def get_app_param(self, name: str, env: Optional[str] = None) -> Optional[str]:
        self._load_all()
        return self._cache.get(self.get_full_path(name, env=env), None)

    def get_shared_param(self, name: str, folder: str, env: Optional[str] = None) -> Optional[str]:
        self._load_all()
        return self._cache.get(self.get_full_path(name, folder=folder, env=env), None)

    def _load_all(self):
        if not self._loaded:
            if isinstance(self._pre_seeded_cache, dict):
                self._cache = self._pre_seeded_cache
            elif isinstance(self._pre_seeded_cache, str) and self._pre_seeded_cache.lower().endswith('.json'):
                with open(self._pre_seeded_cache, 'r') as fin:
                    self._cache = json.load(fin)
