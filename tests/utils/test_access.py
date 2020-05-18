import unittest

from policosm.utils.access import get_access


class AccessTestCase(unittest.TestCase):
    def test_known_country_access(self):
        self.assertEqual(True, get_access('fra', 'tertiary', 'bicycle'))
        self.assertEqual(False, get_access('fra', 'motorway', 'bicycle'))
        self.assertEqual(False, get_access('fra', 'demolished', 'foot'))
        self.assertEqual(True, get_access('fra', 'stairs', 'foot'))

    def test_unknown_country_access(self):
        self.assertEqual(True, get_access('zzz', 'cycleway', 'bicycle'))
        self.assertEqual(True, get_access('zzz', 'space_way', 'bicycle'))


if __name__ == '__main__':
    unittest.main()
