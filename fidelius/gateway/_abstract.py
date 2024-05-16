__all__ = [
    '_BaseFideliusRepo',
    '_BaseFideliusAdminRepo',
]

import re

from .interface import *

from fidelius.structs import *
import logging
log = logging.getLogger(__file__)


class _BaseFideliusRepo(IFideliusRepo, abc.ABC):
    """Covers a lot of basic functionality common across most storage back-ends.
    """

    _APP_PATH_FORMAT = '/fidelius/{group}/{env}/apps/{app}/{name}'
    _SHARED_PATH_FORMAT = '/fidelius/{group}/{env}/shared/{folder}/{name}'

    _EXPRESSION_APP_FORMAT = '${{__FID__:{name}}}'
    _EXPRESSION_SHARED_FORMAT = '${{__FID__:{folder}:{name}}}'

    _EXPRESSION_PATTERN = re.compile(r'\${__FID__:(?:(?P<folder>\w+):)?(?P<name>[\w/-]+)}')

    def __init__(self, app_props: FideliusAppProps, **kwargs):
        log.debug('_BaseFideliusRepo.__init__')
        self._app_props = app_props

        # Any kwargs should have been handled by implementation specific stuff,
        # unless there's a derpy config so let's warn just in case!
        if kwargs:
            for k, v in kwargs.items():
                log.warning(f'AbstractFideliusRepo for some unhandled kwargs: {k}={v}')

    @property
    def app_props(self) -> FideliusAppProps:
        """The current application properties.
        """
        return self._app_props

    def make_app_path(self, env: Optional[str] = None) -> str:
        """The full path to application specific parameters/secrets.
        """
        return self._APP_PATH_FORMAT.format(group=self.app_props.group,
                                            env=env or self.app_props.env,
                                            app=self.app_props.app,
                                            name='{name}')

    def make_shared_path(self, folder: str, env: Optional[str] = None) -> str:
        """The full path to group shared parameters/secrets.
        """
        return self._SHARED_PATH_FORMAT.format(group=self.app_props.group,
                                               env=env or self.app_props.env,
                                               folder=folder,
                                               name='{name}')

    def get_expression_string(self, name: str, folder: Optional[str] = None) -> str:
        """Return a Fidelius expression string (e.g. to use in configuration
        files) which the `replace` method can parse and replace with
        parameters/secrets fetched from the storage backend.

        The default format of these expressions is:
        - `${__FID__:PARAM_NAME}` for app params/secrets
        - `${__FID__:FOLDER:PARAM_NAME}` for shared params/secrets in the given FOLDER

        :param name: The name of the parameter/secret to create an expression for.
        :param folder: Optional name of shared parameters/secrets to use. This
                       is optional and only applies to shared
                       parameters/secrets. Leaving it blank (default) will
                       return the app specific expression.
        :return: The Fidelius expression string.
        """
        if folder:
            return self._EXPRESSION_SHARED_FORMAT.format(name=name, folder=folder)
        else:
            return self._EXPRESSION_APP_FORMAT.format(name=name)

    def get_full_path(self, name: str, folder: Optional[str] = None, env: Optional[str] = None) -> str:
        """Gets the full path to a parameter/secret.

        Parameter/secret paths can be either application specific (use the
        `app_path`) or shared (use the `shared_path`) and this method should
        determine whether to use a shared or app path based on whether or
        not a folder name was given.

        :param name: The name of the parameter/secret to build a path to.
        :param folder: Optional name of shared parameters/secrets to use. This
                       is optional and only applies to shared
                       parameters/secrets. Leaving it blank (default) will
                       return the app specific parameter/secret path.
        :param env: Optional env value override. Defaults to None, which uses
                    the env declaration from the current app properties.
        :return: The full path to a parameter/secret.
        """
        if folder:
            return self.make_shared_path(folder, env=env).format(name=name)
        else:
            return self.make_app_path(env=env).format(name=name)

    def get(self, name: str, folder: Optional[str] = None, no_default: bool = False) -> Optional[str]:
        """Gets the given parameter/secret from the storage this repo uses.

        Parameters/secrets can be either application specific (use the
        `app_path`) or shared (use the `shared_path`) and this method should
        determine whether to get a shared or app parameter based on whether or
        not a folder name was given.

        Unless disabled by the `no_default` parameter, this method will attempt
        to fetch a parameter using the `env=default` if one was not found for
        the env in the current app properties.

        :param name: The name of the parameter/secret to get.
        :param folder: Optional name of shared parameters/secrets to use. This
                       is optional and only applies to shared
                       parameters/secrets. Leaving it blank (default) will
                       return the app specific parameter/secret.
        :param no_default: If True, does not try and get the default value if no
                           value was found for the current set environment.
        :return: The requested parameter/secret or None if it was not found.
        """
        log.debug('_BaseFideliusRepo.get(name=%s, folder=%s, no_default=%s))', name, folder, no_default)
        if folder:
            val = self.get_shared_param(name=name, folder=folder)
            log.debug('_BaseFideliusRepo.get->get_shared_param val=%s', val)
            if val is not None:
                return val

            if no_default:
                log.debug('_BaseFideliusRepo.get->(shared) no_default STOP!')
                return None

            log.debug('_BaseFideliusRepo.get->(shared) Lets try the default!!!')
            return self.get_shared_param(name=name, folder=folder, env='default')
        else:
            val = self.get_app_param(name=name)
            log.debug('_BaseFideliusRepo.get->get_app_param val=%s', val)
            if val is not None:
                return val

            if no_default:
                log.debug('_BaseFideliusRepo.get->(app) no_default STOP!')
                return None

            log.debug('_BaseFideliusRepo.get->(app) Lets try the default!!!')
            return self.get_app_param(name=name, env='default')

    def replace(self, string: str, no_default: bool = False) -> str:
        """Take in a containing a Fidelius parameter/secret configuration
        expression (e.g. read from a config file), parses it, fetches the
        relevant parameter/secret and returns.

        The default format of these expressions is:
        - `${__FID__:PARAM_NAME}` for app params/secrets
        - `${__FID__:FOLDER:PARAM_NAME}` for shared params/secrets in the given FOLDER

        An empty string is returned if the parameter was not found and if the
        string does not match the expression format, it will be returned
        unchanged.

        :param string: The expression to replace with an actual parameter/secret
        :param no_default: If True, does not try and get the default value if no
                           value was found for the current set environment.
        :return: The requested value, an empty string or the original string
        """
        m = self._EXPRESSION_PATTERN.match(string)
        if m:
            return self.get(m.group('name'), m.group('folder'), no_default=no_default) or ''
        return string

    def set_app_path_format(self, new_format: str):
        self._APP_PATH_FORMAT = new_format

    def set_shared_path_format(self, new_format: str):
        self._SHARED_PATH_FORMAT = new_format

    def set_app_expression_format(self, new_format: str):
        self._EXPRESSION_APP_FORMAT = new_format

    def set_shared_expression_format(self, new_format: str):
        self._EXPRESSION_SHARED_FORMAT = new_format

    def set_expression_pattern(self, new_format: Union[str, re.Pattern]):
        if isinstance(new_format, str):
            new_format = re.compile(new_format)
        self._EXPRESSION_PATTERN = new_format


class _BaseFideliusAdminRepo(_BaseFideliusRepo, IFideliusAdminRepo, abc.ABC):
    """Covers a lot of admin basic functionality common across most storage back-ends.
    """
    def __init__(self, app_props: FideliusAppProps, tags: Optional[FideliusTags] = None, **kwargs):
        log.debug('_BaseFideliusAdminRepo.__init__ (this should set tags?!?)')
        super().__init__(app_props, **kwargs)
        self._tags = tags

    @property
    def tags(self) -> Optional[FideliusTags]:
        return self._tags

    def set_env(self, env: str):
        self.app_props.env = env
