__all__ = [
    'IFideliusRepo',
    'IFideliusAdminRepo',
]
import abc
from fidelius.structs import *


class IFideliusRepo(abc.ABC):
    @abc.abstractmethod
    def __init__(self, app_props: FideliusAppProps, **kwargs):
        """Initialise a new Fidelius Repository.

        :param app_props: The application properties to use.
        """
        pass

    @property
    @abc.abstractmethod
    def app_props(self) -> FideliusAppProps:
        """The current application properties.
        """
        pass

    @abc.abstractmethod
    def make_app_path(self, env: Optional[str] = None) -> str:
        """The full path to application specific parameters/secrets.
        """
        pass

    @abc.abstractmethod
    def make_shared_path(self, folder: str, env: Optional[str] = None) -> str:
        """The full path to group shared parameters/secrets.
        """
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def get_app_param(self, name: str, env: Optional[str] = None) -> Optional[str]:
        """Gets an application specific parameter/secret.

        :param name: The name of the parameter/secret to get.
        :param env: Optional env value override. Defaults to None, which uses
                    the env declaration from the current app properties.
        :return: The requested parameter/secret or None if it was not found.
        """
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def get_shared_param(self, name: str, folder: str, env: Optional[str] = None) -> Optional[str]:
        """Gets a group shared parameter/secret.

        :param name: The name of the parameter/secret to get.
        :param folder: The folder where the group shared parameter/secret is
                       located.
        :param env: Optional env value override. Defaults to None, which uses
                    the env declaration from the current app properties.
        :return: The requested parameter/secret or None if it was not found.
        """
        pass

    @abc.abstractmethod
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
        pass


class IFideliusAdminRepo(IFideliusRepo):
    @abc.abstractmethod
    def __init__(self, app_props: FideliusAppProps, tags: Optional[FideliusTags] = None, **kwargs):
        """Initialise a new Fidelius Admin Repository.

        :param app_props: The application properties to use.
        :param tags: An optional set of meta-data tags to use when creating new
                     parameters (if supported by the underlying
                     parameter/secret storage). Note that updating a parameter
                     does not update/change tags, they are only applied when
                     creating new parameters!
        """
        pass

    @property
    @abc.abstractmethod
    def tags(self) -> Optional[FideliusTags]:
        """The tags to use when creating new parameters.
        """
        pass

    @abc.abstractmethod
    def set_env(self, env: str):
        """Sets the current app properties env to something else (for admin purposes)
        """
        pass

    @abc.abstractmethod
    def create_param(self, name: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Creates a new unencrypted application parameter.

        :param name: The parameter name.
        :param value: The parameter value.
        :param description: An optional description of the parameter (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the parameters full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def update_param(self, name: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Updates an existing unencrypted application parameter.

        :param name: The parameter name.
        :param value: The parameter value.
        :param description: An optional description of the parameter (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the parameters full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def delete_param(self, name: str, env: Optional[str] = None):
        """Deletes an existing unencrypted application parameter.

        :param name: The parameter name.
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        """
        pass

    @abc.abstractmethod
    def create_shared_param(self, name: str, folder: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Creates a new unencrypted group-shared parameter under the given
        shared folder.

        :param name: The parameter name.
        :param folder: The shared folder to place the parameter under.
        :param value: The parameter value.
        :param description: An optional description of the parameter (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the parameters full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def update_shared_param(self, name: str, folder: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Updates an existing unencrypted group-shared parameter under the
        given shared folder.

        :param name: The parameter name.
        :param folder: The shared folder to place the parameter under.
        :param value: The parameter value.
        :param description: An optional description of the parameter (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the parameters full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def delete_shared_param(self, name: str, folder: str, env: Optional[str] = None):
        """Deletes an existing unencrypted group-shared parameter under the
        given shared folder.

        :param name: The parameter name.
        :param folder: The shared folder parameter is placed under.
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        """
        pass

    @abc.abstractmethod
    def create_secret(self, name: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Creates a new encrypted application secret.

        :param name: The secret name.
        :param value: The secret value.
        :param description: An optional description of the secret (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the secret full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def update_secret(self, name: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Updates an existing encrypted application secret.

        :param name: The secret name.
        :param value: The secret value.
        :param description: An optional description of the secret (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the secret full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def delete_secret(self, name: str, env: Optional[str] = None):
        """Deletes an existing encrypted application secret.

        :param name: The parameter name.
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        """
        pass

    @abc.abstractmethod
    def create_shared_secret(self, name: str, folder: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Creates a new encrypted group-shared secret under the given
        shared folder.

        :param name: The secret name.
        :param folder: The shared folder to place the secret under.
        :param value: The secret value.
        :param description: An optional description of the parameter (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the secret full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def update_shared_secret(self, name: str, folder: str, value: str, description: Optional[str] = None, env: Optional[str] = None) -> (str, str):
        """Updates an existing encrypted group-shared secret under the
        given shared folder.

        :param name: The secret name.
        :param folder: The shared folder to place the secret under.
        :param value: The secret value.
        :param description: An optional description of the parameter (if
                            supported by the underlying parameter/secret
                            storage)
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        :return: A two tuple of strings containing the secret full path and
                 the default suggested configuration expression to use (for
                 convenience, which the `replace` method can parse "as-is")
        """
        pass

    @abc.abstractmethod
    def delete_shared_secret(self, name: str, folder: str, env: Optional[str] = None):
        """Deletes an existing encrypted group-shared secret under the
        given shared folder.

        :param name: The secret name.
        :param folder: The shared folder secret is placed under.
        :param env: Optional env value override. Defaults to None, which uses
                    the env from the current app properties.
        """
        pass
