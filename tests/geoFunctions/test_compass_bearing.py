import unittest

from shapely.geometry import LineString

from policosm.geoFunctions.compass_bearing import average_compass_bearing_line


class CompassBearingTest(unittest.TestCase):
    def test_something(self):
        line = LineString([(0.0, 0.0), (0.0, 1.0)])
        angle = average_compass_bearing_line(line)
        self.assertEqual(0.0, angle)

        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        angle = average_compass_bearing_line(line)
        self.assertEqual(45.0, angle)

        line = LineString([(0.0, 0.0), (-1.0, -1.0)])
        angle = average_compass_bearing_line(line)
        self.assertEqual(225.0, angle)

        line = LineString([(0.0, 0.0), (1.0, 0.0), (2.0, 0), (2.0, 1.0), (1.0, 1.0), (0.0, 1.0), (0.0, 2.0)])
        angle = average_compass_bearing_line(line)
        print(angle)
        self.assertEqual(0.0, angle)


if __name__ == '__main__':
    unittest.main()
