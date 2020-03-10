import unittest

from policosm.utils.levels import get_level


class LevelsTestCase(unittest.TestCase):
    def test_known(self):
        for highway in ['construction', 'demolished', 'raceway', 'abandoned', 'disused', 'foo', 'no','projected', 'planned','proposed','razed','dismantled','historic']:
            self.assertEqual(0, get_level(highway))
        for highway in ['stairway', 'elevator', 'corridor', 'hallway', 'slide']:
            self.assertEqual(1, get_level(highway))
        for highway in ['services', 'busway', 'bus_guideway', 'access','bus_stop', 'via_ferrata', 'access_ramp', 'emergency_access_point', 'emergency_bay','service', 'footway',
         'traffic_island', 'virtual', 'cyleway', 'cycleway', 'byway', 'path', 'track', 'pedestrian', 'steps',
         'platform', 'bridleway', 'rest_area', 'escape','footway']:
            self.assertEqual(2, get_level(highway))
        for highway in  ['residential', 'yes', 'unclassified', 'crossing', 'unknown',
         'bridge', 'lane', 'ford', 'psv', 'living_street','alley']:
            self.assertEqual(3, get_level(highway))
        for highway in ['tertiary', 'tertiary_link', 'turning_circle', 'road', 'roundabout', 'ice_road']:
            self.assertEqual(4, get_level(highway))
        for highway in ['secondary', 'secondary_link']:
            self.assertEqual(5, get_level(highway))
        for highway in ['primary', 'primary_link']:
            self.assertEqual(6, get_level(highway))
        for highway in ['trunk', 'trunk_link']:
            self.assertEqual(7, get_level(highway))
        for highway in ['motorway', 'motorway_link','ramp']:
            self.assertEqual(8, get_level(highway))

    def test_unknown(self):
        self.assertEqual(3, get_level('zzz'))


if __name__ == '__main__':
    unittest.main()
