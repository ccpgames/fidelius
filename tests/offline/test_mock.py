import unittest

from fidelius.fideliusapi import *

import logging
log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

_APP_PROPS = FideliusAppProps(app='mock-app', group='somegroup', env='mock')
_APP_PROPS_TWO = FideliusAppProps(app='other-app', group='somegroup', env='mock')
_APP_PROPS_THREE = FideliusAppProps(app='mock-app', group='somegroup', env='test')

from fidelius.gateway.mock._inmemcache import _SingletonDict  # noqa


def _clear_cache():
    _SingletonDict().clear()


class TestMock(unittest.TestCase):
    def test_mock(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        fia.create_param('DB_NAME', 'brain')
        fia.create_secret('DB_PASSWORD', 'myBADpassword')
        fia.create_shared_param('DB_HOST', 'dbstuff', 'braindb.mock.cc')
        fia.create_shared_secret('DB_USERNAME', 'dbstuff', 'svc-mock')

        fid = FideliusFactory.get_class('mock')(_APP_PROPS)
        self.assertIsNone(fid.get('mock-value'))
        self.assertEqual('brain', fid.get('DB_NAME'))
        self.assertEqual('myBADpassword', fid.get('DB_PASSWORD'))
        self.assertEqual('braindb.mock.cc', fid.get('DB_HOST', 'dbstuff'))
        self.assertEqual('svc-mock', fid.get('DB_USERNAME', 'dbstuff'))
        _clear_cache()

    def test_mock_admin_params(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        self.assertIsNone(fia.get('DB_PASSWORD'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_param('DB_PASSWORD')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_param('DB_PASSWORD', 'myBADpassword')

        key, expression = fia.create_param('DB_PASSWORD', 'myBADpassword')
        self.assertEqual('/fidelius/somegroup/mock/apps/mock-app/DB_PASSWORD', key)
        self.assertEqual('${__FID__:DB_PASSWORD}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_param('DB_PASSWORD', 'myWORSEpassword')

        key, expression = fia.update_param('DB_PASSWORD', 'myWORSEpassword')
        self.assertEqual('/fidelius/somegroup/mock/apps/mock-app/DB_PASSWORD', key)
        self.assertEqual('${__FID__:DB_PASSWORD}', expression)

        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD'))

        fia.delete_param('DB_PASSWORD')

        self.assertIsNone(fia.get('DB_PASSWORD'))
        _clear_cache()

    def test_mock_admin_secrets(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        self.assertIsNone(fia.get('DB_PASSWORD'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_secret('DB_PASSWORD')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_secret('DB_PASSWORD', 'myBADpassword')

        key, expression = fia.create_secret('DB_PASSWORD', 'myBADpassword')
        self.assertEqual('/fidelius/somegroup/mock/apps/mock-app/DB_PASSWORD', key)
        self.assertEqual('${__FID__:DB_PASSWORD}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_secret('DB_PASSWORD', 'myWORSEpassword')

        key, expression = fia.update_secret('DB_PASSWORD', 'myWORSEpassword')
        self.assertEqual('/fidelius/somegroup/mock/apps/mock-app/DB_PASSWORD', key)
        self.assertEqual('${__FID__:DB_PASSWORD}', expression)

        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD'))

        fia.delete_secret('DB_PASSWORD')

        self.assertIsNone(fia.get('DB_PASSWORD'))
        _clear_cache()

    def test_mock_admin_shared_params(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        fia2 = FideliusFactory.get_admin_class('mock')(_APP_PROPS_TWO)
        self.assertIsNone(fia.get('DB_PASSWORD', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD', 'dbfolder'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_shared_param('DB_PASSWORD', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.delete_shared_param('DB_PASSWORD', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_shared_param('DB_PASSWORD', 'dbfolder', 'myBADpassword')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.update_shared_param('DB_PASSWORD', 'dbfolder', 'myBADpassword')

        key, expression = fia.create_shared_param('DB_PASSWORD', 'dbfolder', 'myBADpassword')
        self.assertEqual('/fidelius/somegroup/mock/shared/dbfolder/DB_PASSWORD', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD', 'dbfolder'))
        self.assertEqual('myBADpassword', fia2.get('DB_PASSWORD', 'dbfolder'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_shared_param('DB_PASSWORD', 'dbfolder', 'myWORSEpassword')

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia2.create_shared_param('DB_PASSWORD', 'dbfolder', 'myWORSEpassword')

        key, expression = fia2.update_shared_param('DB_PASSWORD', 'dbfolder', 'myWORSEpassword')
        self.assertEqual('/fidelius/somegroup/mock/shared/dbfolder/DB_PASSWORD', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD}', expression)

        self.assertEqual('myWORSEpassword', fia2.get('DB_PASSWORD', 'dbfolder'))
        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD', 'dbfolder'))

        fia.delete_shared_param('DB_PASSWORD', 'dbfolder')

        self.assertIsNone(fia.get('DB_PASSWORD', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD', 'dbfolder'))
        _clear_cache()

    def test_mock_admin_shared_secrets(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        fia2 = FideliusFactory.get_admin_class('mock')(_APP_PROPS_TWO)
        self.assertIsNone(fia.get('DB_PASSWORD', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD', 'dbfolder'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_shared_secret('DB_PASSWORD', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.delete_shared_secret('DB_PASSWORD', 'dbfolder')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_shared_secret('DB_PASSWORD', 'dbfolder', 'myBADpassword')

        with self.assertRaises(FideliusParameterNotFound):
            fia2.update_shared_secret('DB_PASSWORD', 'dbfolder', 'myBADpassword')

        key, expression = fia.create_shared_secret('DB_PASSWORD', 'dbfolder', 'myBADpassword')
        self.assertEqual('/fidelius/somegroup/mock/shared/dbfolder/DB_PASSWORD', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD}', expression)

        self.assertEqual('myBADpassword', fia.get('DB_PASSWORD', 'dbfolder'))
        self.assertEqual('myBADpassword', fia2.get('DB_PASSWORD', 'dbfolder'))

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia.create_shared_secret('DB_PASSWORD', 'dbfolder', 'myWORSEpassword')

        with self.assertRaises(FideliusParameterAlreadyExists):
            fia2.create_shared_secret('DB_PASSWORD', 'dbfolder', 'myWORSEpassword')

        key, expression = fia2.update_shared_secret('DB_PASSWORD', 'dbfolder', 'myWORSEpassword')
        self.assertEqual('/fidelius/somegroup/mock/shared/dbfolder/DB_PASSWORD', key)
        self.assertEqual('${__FID__:dbfolder:DB_PASSWORD}', expression)

        self.assertEqual('myWORSEpassword', fia2.get('DB_PASSWORD', 'dbfolder'))
        self.assertEqual('myWORSEpassword', fia.get('DB_PASSWORD', 'dbfolder'))

        fia.delete_shared_secret('DB_PASSWORD', 'dbfolder')

        self.assertIsNone(fia.get('DB_PASSWORD', 'dbfolder'))
        self.assertIsNone(fia2.get('DB_PASSWORD', 'dbfolder'))
        _clear_cache()

    def test_mock_defaults(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        fia.create_param('DB_NAME', 'brain', env='default')
        fia.create_secret('DB_PASSWORD', 'defaultPassword', env='default')
        fia.create_shared_param('DB_HOST', 'dbstuff', 'braindb.localhost', env='default')
        fia.create_shared_secret('DB_USERNAME', 'dbstuff', 'svc-mock', env='default')

        fia.create_secret('DB_PASSWORD', 'mockPassword')
        fia.create_shared_param('DB_HOST', 'dbstuff', 'braindb.mock.cc')

        fid = FideliusFactory.get_class('mock')(_APP_PROPS)
        self.assertIsNone(fid.get('mock-value'))
        self.assertEqual('brain', fid.get('DB_NAME'))
        self.assertEqual('mockPassword', fid.get('DB_PASSWORD'))
        self.assertEqual('braindb.mock.cc', fid.get('DB_HOST', 'dbstuff'))
        self.assertEqual('svc-mock', fid.get('DB_USERNAME', 'dbstuff'))

        fid2 = FideliusFactory.get_class('mock')(_APP_PROPS_THREE)
        self.assertIsNone(fid2.get('mock-value'))
        self.assertEqual('brain', fid2.get('DB_NAME'))
        self.assertEqual('defaultPassword', fid2.get('DB_PASSWORD'))
        self.assertEqual('braindb.localhost', fid2.get('DB_HOST', 'dbstuff'))
        self.assertEqual('svc-mock', fid2.get('DB_USERNAME', 'dbstuff'))

        self.assertIsNone(fid.get('DB_NAME', no_default=True))
        self.assertEqual('mockPassword', fid.get('DB_PASSWORD', no_default=True))
        self.assertEqual('braindb.mock.cc', fid.get('DB_HOST', 'dbstuff', no_default=True))
        self.assertIsNone(fid.get('DB_USERNAME', 'dbstuff', no_default=True))
        _clear_cache()

    def test_mock_replacer(self):
        _clear_cache()
        fia = FideliusFactory.get_admin_class('mock')(_APP_PROPS)
        fia.create_param('DB_NAME', 'brain')
        fia.create_secret('DB_PASSWORD', 'myBADpassword')
        fia.create_shared_param('DB_HOST', 'dbstuff', 'braindb.mock.cc')
        fia.create_shared_secret('DB_USERNAME', 'dbstuff', 'svc-mock')

        fid = FideliusFactory.get_class('mock')(_APP_PROPS)
        self.assertEqual('brain', fid.replace('${__FID__:DB_NAME}'))
        self.assertEqual('myBADpassword', fid.replace('${__FID__:DB_PASSWORD}'))
        self.assertEqual('braindb.mock.cc', fid.replace('${__FID__:dbstuff:DB_HOST}'))
        self.assertEqual('svc-mock', fid.replace('${__FID__:dbstuff:DB_USERNAME}'))
        self.assertEqual('', fid.replace('${__FID__:I_DONT_EXIST}'))
        self.assertEqual('I am incorrectly formatted!', fid.replace('I am incorrectly formatted!'))
        _clear_cache()
