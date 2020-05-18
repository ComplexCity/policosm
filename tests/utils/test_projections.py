import unittest

from policosm.utils.projections import get_most_accurate_epsg


class ProjectionsTestCase(unittest.TestCase):
    def test_non_utm(self):
        mumbai = (72.88261, 19.07283)
        self.assertEqual(32643, get_most_accurate_epsg(mumbai))

    def test_utm(self):
        las_vegas = (-115.13722, 36.17497)
        self.assertEqual(3607, get_most_accurate_epsg(las_vegas))
        paris = (2.320582, 48.859489)
        self.assertEqual(3949, get_most_accurate_epsg(paris))


if __name__ == '__main__':
    unittest.main()
