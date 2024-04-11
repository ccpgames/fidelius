__all__ = [
    'FideliusError',
    'FideliusAdminError',
    'FideliusParameterNotFound',
    'FideliusParameterAlreadyExists',
]


class FideliusError(Exception):
    pass


class FideliusAdminError(FideliusError):
    pass


class FideliusParameterNotFound(FideliusAdminError, KeyError):
    pass


class FideliusParameterAlreadyExists(FideliusAdminError, ValueError):
    pass
