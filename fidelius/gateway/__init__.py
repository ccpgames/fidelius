__all__ = [
    'FideliusFactory',
]

from fidelius.structs import *
from .interface import *
from ccptools.tpu import strimp

import logging
log = logging.getLogger(__name__)


class FideliusFactory:
    @staticmethod
    def get_class(impl: str = 'paramstore') -> Type[IFideliusRepo]:
        return strimp.get_class(f'fidelius.gateway.{impl}._std.FideliusRepo', logger=log, reraise=True)

    @staticmethod
    def get_admin_class(impl: str = 'paramstore') -> Type[IFideliusAdminRepo]:
        return strimp.get_class(f'fidelius.gateway.{impl}._std.FideliusAdmin', logger=log, reraise=True)
