__all__ = [
    'VaultResponse',
    'VaultResponseData',
    'VaultResponseMetadata',
]

from ccptools.structs import *
from fidelius.utils import SelfResolvingFromDictDataclass


@dataclasses.dataclass
class VaultResponseMetadata(SelfResolvingFromDictDataclass):
    created_time: Optional[Datetime] = None
    custom_metadata: Any = None
    deletion_time: Optional[Datetime] = None
    destroyed: bool = False
    version: Optional[int] = None


@dataclasses.dataclass
class VaultResponseData(SelfResolvingFromDictDataclass):
    data: Dict[str, str] = dataclasses.field(default_factory=dict)
    metadata: Optional[VaultResponseMetadata] = None


@dataclasses.dataclass
class VaultResponse(SelfResolvingFromDictDataclass):
    request_id: str = ''
    lease_id: Optional[str] = ''
    renewable: bool = False
    lease_duration: Optional[int] = None
    data: Optional[VaultResponseData] = None
    wrap_info: Optional[Any] = None
    warnings: Optional[Any] = None
    auth: Optional[Any] = None
    mount_type: Optional[str] = None

    def get_keyval(self, key: str) -> Optional[str]:
        if isinstance(self.data, VaultResponseData):
            if isinstance(self.data.data, dict):
                return self.data.data.get(key, None)
        return None


