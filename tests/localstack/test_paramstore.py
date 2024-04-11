import unittest

from fidelius.fideliusapi import *
from typing import *

import os

import logging
log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

_APP_PROPS = FideliusAppProps(app='mock-app', group='tempunittestgroup', env='mock')
_APP_PROPS_TWO = FideliusAppProps(app='other-app', group='tempunittestgroup', env='mock')
_APP_PROPS_THREE = FideliusAppProps(app='mock-app', group='tempunittestgroup', env='test')


def _extract_param_names(response: Dict) -> List[str]:
    return [p.get('Name') for p in response.get('Parameters', [])]


def _get_param_names_by_path(ssm, path: str) -> List[str]:
    return _extract_param_names(ssm.get_parameters_by_path(Path=path,
                                                           Recursive=True,
                                                           WithDecryption=False))


def _delete_all_params():
    fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
    ssm = fia._ssm  # noqa
    paths = [
        '/fidelius/tempunittestgroup/',
    ]
    param_set = set()
    for p in paths:
        param_set.update(_get_param_names_by_path(ssm, p))

    if param_set:
        res = ssm.delete_parameters(Names=list(param_set))
        log.debug('_delete_all_params -> %s', res)


class TestParamstore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Check if certain environment variables are set
        env_var = os.getenv('FIDELIUS_AWS_ENDPOINT_URL')
        if not env_var:
            raise unittest.SkipTest("Environment variable 'FIDELIUS_AWS_ENDPOINT_URL' not set. "
                                    "Skipping all tests in TestParamstore.")
        # Just in case...!
        _delete_all_params()

    def test_paramstore(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        fia.create_param('MY_DB_NAME', 'brain')
        fia.create_secret('MY_DB_PASSWORD', 'myBADpassword')
        fia.create_shared_param('MY_DB_HOST', 'dbstuff', 'braindb.mock.cc')
        fia.create_shared_secret('MY_DB_USERNAME', 'dbstuff', 'svc-mock')

        fid = FideliusFactory.get_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        self.assertIsNone(fid.get('mock-value'))
        self.assertEqual('brain', fid.get('MY_DB_NAME'))
        self.assertEqual('myBADpassword', fid.get('MY_DB_PASSWORD'))
        self.assertEqual('braindb.mock.cc', fid.get('MY_DB_HOST', 'dbstuff'))
        self.assertEqual('svc-mock', fid.get('MY_DB_USERNAME', 'dbstuff'))
        _delete_all_params()

    def test_paramstore_admin_params(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        self.assertIsNone(fia.get('DB_PASSWORD_TWO'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_param('DB_PASSWORD_TWO')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_param('DB_PASSWORD_TWO', 'myBADpassword')

        key, expression = fia.create_param('DB_PASSWORD_TWO', 'myBADpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/apps/mock-app/DB_PASSWORD_TWO', key)
        self.assertEqual('${__FID__:DB_PASSWORD_TWO}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD_TWO'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_param('DB_PASSWORD_TWO', 'myWORSEpassword')

        key, expression = fia.update_param('DB_PASSWORD_TWO', 'myWORSEpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/apps/mock-app/DB_PASSWORD_TWO', key)
        self.assertEqual('${__FID__:DB_PASSWORD_TWO}', expression)

        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD_TWO'))

        fia.delete_param('DB_PASSWORD_TWO')

        self.assertIsNone(fia.get('DB_PASSWORD_TWO'))
        _delete_all_params()

    def test_paramstore_admin_secrets(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        self.assertIsNone(fia.get('DB_PASSWORD_THREE'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_secret('DB_PASSWORD_THREE')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_secret('DB_PASSWORD_THREE', 'myBADpassword')

        key, expression = fia.create_secret('DB_PASSWORD_THREE', 'myBADpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/apps/mock-app/DB_PASSWORD_THREE', key)
        self.assertEqual('${__FID__:DB_PASSWORD_THREE}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD_THREE'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_secret('DB_PASSWORD_THREE', 'myWORSEpassword')

        key, expression = fia.update_secret('DB_PASSWORD_THREE', 'myWORSEpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/apps/mock-app/DB_PASSWORD_THREE', key)
        self.assertEqual('${__FID__:DB_PASSWORD_THREE}', expression)

        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD_THREE'))

        fia.delete_secret('DB_PASSWORD_THREE')

        self.assertIsNone(fia.get('DB_PASSWORD_THREE'))
        _delete_all_params()

    def test_paramstore_admin_shared_params(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        fia2 = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS_TWO, flush_cache_every_time=True)
        self.assertIsNone(fia.get('DB_PASSWORD_FOUR', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD_FOUR', 'dbfolder'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_shared_param('DB_PASSWORD_FOUR', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.delete_shared_param('DB_PASSWORD_FOUR', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_shared_param('DB_PASSWORD_FOUR', 'dbfolder', 'myBADpassword')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.update_shared_param('DB_PASSWORD_FOUR', 'dbfolder', 'myBADpassword')

        key, expression = fia.create_shared_param('DB_PASSWORD_FOUR', 'dbfolder', 'myBADpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/shared/dbfolder/DB_PASSWORD_FOUR', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD_FOUR}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD_FOUR', 'dbfolder'))
        self.assertEqual('myBADpassword', fia2.get('DB_PASSWORD_FOUR', 'dbfolder'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_shared_param('DB_PASSWORD_FOUR', 'dbfolder', 'myWORSEpassword')

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia2.create_shared_param('DB_PASSWORD_FOUR', 'dbfolder', 'myWORSEpassword')

        key, expression = fia2.update_shared_param('DB_PASSWORD_FOUR', 'dbfolder', 'myWORSEpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/shared/dbfolder/DB_PASSWORD_FOUR', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD_FOUR}', expression)

        self.assertEqual('myWORSEpassword', fia2.get('DB_PASSWORD_FOUR', 'dbfolder'))
        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD_FOUR', 'dbfolder'))

        fia.delete_shared_param('DB_PASSWORD_FOUR', 'dbfolder')

        self.assertIsNone(fia.get('DB_PASSWORD_FOUR', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD_FOUR', 'dbfolder'))
        _delete_all_params()

    def test_paramstore_admin_shared_secrets(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        fia2 = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS_TWO, flush_cache_every_time=True)
        self.assertIsNone(fia.get('DB_PASSWORD_FIVE', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD_FIVE', 'dbfolder'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_shared_secret('DB_PASSWORD_FIVE', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.delete_shared_secret('DB_PASSWORD_FIVE', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_shared_secret('DB_PASSWORD_FIVE', 'dbfolder', 'myBADpassword')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.update_shared_secret('DB_PASSWORD_FIVE', 'dbfolder', 'myBADpassword')

        key, expression = fia.create_shared_secret('DB_PASSWORD_FIVE', 'dbfolder', 'myBADpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/shared/dbfolder/DB_PASSWORD_FIVE', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD_FIVE}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD_FIVE', 'dbfolder'))
        self.assertEqual('myBADpassword', fia2.get('DB_PASSWORD_FIVE', 'dbfolder'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_shared_secret('DB_PASSWORD_FIVE', 'dbfolder', 'myWORSEpassword')

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia2.create_shared_secret('DB_PASSWORD_FIVE', 'dbfolder', 'myWORSEpassword')

        key, expression = fia2.update_shared_secret('DB_PASSWORD_FIVE', 'dbfolder', 'myWORSEpassword')
        self.assertEqual('/fidelius/tempunittestgroup/mock/shared/dbfolder/DB_PASSWORD_FIVE', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD_FIVE}', expression)

        self.assertEqual('myWORSEpassword', fia2.get('DB_PASSWORD_FIVE', 'dbfolder'))
        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD_FIVE', 'dbfolder'))

        fia.delete_shared_secret('DB_PASSWORD_FIVE', 'dbfolder')

        self.assertIsNone(fia.get('DB_PASSWORD_FIVE', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD_FIVE', 'dbfolder'))
        _delete_all_params()

    def test_paramstore_defaults(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        fia.create_param('DB_NAME', 'brain', env='default')
        fia.create_secret('DB_PASSWORD', 'defaultPassword', env='default')
        fia.create_shared_param('DB_HOST', 'dbstuff', 'braindb.localhost', env='default')
        fia.create_shared_secret('DB_USERNAME', 'dbstuff', 'svc-mock', env='default')

        fia.create_secret('DB_PASSWORD', 'mockPassword')
        fia.create_shared_param('DB_HOST', 'dbstuff', 'braindb.mock.cc')

        fid = FideliusFactory.get_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        self.assertIsNone(fid.get('mock-value'))
        self.assertEqual('brain', fid.get('DB_NAME'))
        self.assertEqual('mockPassword', fid.get('DB_PASSWORD'))
        self.assertEqual('braindb.mock.cc', fid.get('DB_HOST', 'dbstuff'))
        self.assertEqual('svc-mock', fid.get('DB_USERNAME', 'dbstuff'))

        fid2 = FideliusFactory.get_class('paramstore')(_APP_PROPS_THREE, flush_cache_every_time=True)
        self.assertIsNone(fid2.get('mock-value'))
        self.assertEqual('brain', fid2.get('DB_NAME'))
        self.assertEqual('defaultPassword', fid2.get('DB_PASSWORD'))
        self.assertEqual('braindb.localhost', fid2.get('DB_HOST', 'dbstuff'))
        self.assertEqual('svc-mock', fid2.get('DB_USERNAME', 'dbstuff'))

        self.assertIsNone(fid.get('DB_NAME', no_default=True))
        self.assertEqual('mockPassword', fid.get('DB_PASSWORD', no_default=True))
        self.assertEqual('braindb.mock.cc', fid.get('DB_HOST', 'dbstuff', no_default=True))
        self.assertIsNone(fid.get('DB_USERNAME', 'dbstuff', no_default=True))
        _delete_all_params()

    def test_paramstore_replacer(self):
        fia = FideliusFactory.get_admin_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        fia.create_param('DB2_NAME', 'brain')
        fia.create_secret('DB2_PASSWORD', 'myBADpassword')
        fia.create_shared_param('DB2_HOST', 'dbstuff', 'braindb.mock.cc')
        fia.create_shared_secret('DB2_USERNAME', 'dbstuff', 'svc-mock')

        fid = FideliusFactory.get_class('paramstore')(_APP_PROPS, flush_cache_every_time=True)
        self.assertEqual('brain', fid.replace('${__FID__:DB2_NAME}'))
        self.assertEqual('myBADpassword', fid.replace('${__FID__:DB2_PASSWORD}'))
        self.assertEqual('braindb.mock.cc', fid.replace('${__FID__:dbstuff:DB2_HOST}'))
        self.assertEqual('svc-mock', fid.replace('${__FID__:dbstuff:DB2_USERNAME}'))
        self.assertEqual('', fid.replace('${__FID__:I_DONT_EXIST}'))
        self.assertEqual('I am incorrectly formatted!', fid.replace('I am incorrectly formatted!'))
        _delete_all_params()
