__all__ = [
    'fidelius_replace',
]
import re
from fidelius.gateway.paramstore import ParameterStore

_VAR_PATTERN = re.compile(r'\${__FID__:(?:(?P<shared_group>\w+):)?(?P<name>[\w/-]+)}')


def fidelius_replace(value: str, pmstore: ParameterStore) -> str:
    m = _VAR_PATTERN.match(value)
    if m:
        return pmstore.get(m.group('name'), m.group('shared_group'))
    return value

