import unittest

from fidelius.gateway.mock._inmemcache import _SingletonDict  # noqa

import logging
log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)


class TestSingletonDict(unittest.TestCase):
    def test_singleton_dict(self):
        d = _SingletonDict()
        d.clear()  # Just in case!

        d2 = _SingletonDict()

        self.assertFalse(bool(d))
        self.assertFalse(bool(d2))

        self.assertFalse('foo' in d)
        self.assertFalse('foo' in d2)

        self.assertIsNone(d.get('foo'))
        self.assertIsNone(d2.get('foo'))

        with self.assertRaises(KeyError):
            _ = d['foo']

        with self.assertRaises(KeyError):
            _ = d2['foo']

        d['foo'] = 'bar'

        self.assertTrue(bool(d))
        self.assertTrue(bool(d2))

        self.assertTrue('foo' in d)
        self.assertTrue('foo' in d2)

        self.assertEqual('bar', d.get('foo'))
        self.assertEqual('bar', d2.get('foo'))

        self.assertEqual('bar', d['foo'])
        self.assertEqual('bar', d2['foo'])

        d3 = _SingletonDict()

        self.assertTrue(bool(d3))
        self.assertTrue('foo' in d3)
        self.assertEqual('bar', d3.get('foo'))
        self.assertEqual('bar', d3['foo'])

        d3['foo'] = 'not bar'

        self.assertEqual('not bar', d['foo'])
        self.assertEqual('not bar', d2['foo'])
        self.assertEqual('not bar', d3['foo'])

        del d2['foo']

        self.assertFalse(bool(d))
        self.assertFalse(bool(d2))
        self.assertFalse(bool(d3))

        self.assertFalse('foo' in d)
        self.assertFalse('foo' in d2)
        self.assertFalse('foo' in d3)

        self.assertIsNone(d.get('foo'))
        self.assertIsNone(d2.get('foo'))
        self.assertIsNone(d3.get('foo'))

        with self.assertRaises(KeyError):
            _ = d['foo']

        with self.assertRaises(KeyError):
            _ = d2['foo']

        with self.assertRaises(KeyError):
            _ = d3['foo']
