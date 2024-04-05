__all__ = [
    'Tags',
]
from ._base import *


class Tags:
    __slots__ = ('application', 'owner', 'tier', 'finance', '_other')

    def __init__(self, application: str, owner: str, tier: str = 'default', finance: str = 'COST', **kwargs):
        self.application = application
        self.owner = owner
        self.tier = tier
        self.finance = finance
        self._other = kwargs or {}

    def __getattr__(self, name: str) -> Optional[str]:
        return self._other.get(name, None)

    def __setattr__(self, name: str, value: Optional[str]):
        if name in self.__slots__:
            if value is None:
                raise ValueError(f'tag "{name}" needs a string value')
            object.__setattr__(self, name, value)
        else:
            if value is None:
                if name in self._other:
                    del self._other[name]
            else:
                self._other[name] = value

    def __delattr__(self, name: str):
        self.__setattr__(name, None)

    def to_dict(self) -> Dict[str, str]:
        d = {
            'application': self.application,
            'owner': self.owner,
            'tier': self.tier,
            'finance': self.finance
        }
        if self._other:
            d.update(self._other)
        return d

    def to_aws_format(self) -> List[Dict[str, str]]:
        return [{'Key': k, 'Value': v} for k, v in self.to_dict().items()]
