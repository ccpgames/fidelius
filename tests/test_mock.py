import unittest

from fidelius.fideliusapi import *

_app_props = FideliusAppProps(app='mock-app', group='somegroup', env='mock')


class TestMock(unittest.TestCase):
    def test_mock(self):
        fid = FideliusFactory.get_class('mock')(_app_props)
        self.assertEqual('L2ZpZGVsaXVzL3NvbWVncm91cC9tb2NrL2FwcHMvbW9jay1hcHAvbW9jay12YWx1ZQ==', fid.get('mock-value'))
        self.assertEqual('L2ZpZGVsaXVzL3NvbWVncm91cC9tb2NrL2FwcHMvbW9jay1hcHAvREJfUEFTU1dPUkQ=', fid.get('DB_PASSWORD'))
        self.assertEqual('L2ZpZGVsaXVzL3NvbWVncm91cC9tb2NrL3NoYXJlZC9zaGFyZWRwb3N0Z3Jlcy9EQl9IT1NU', fid.get('DB_HOST', 'sharedpostgres'))

    def test_mock_admin(self):
        fia = FideliusFactory.get_admin_class('mock')(_app_props)
        self.assertIsNone(fia.get('DB_PASSWORD'))

        with self.assertRaises(FideliusParameterNotFound):
            fia.delete_param('DB_PASSWORD')

        with self.assertRaises(FideliusParameterNotFound):
            fia.update_param('DB_PASSWORD', 'myBADpassword')

        key, expression = fia.create_param('DB_PASSWORD', 'myBADpassword')

