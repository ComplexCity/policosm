import unittest

from policosm.utils.bicycles import get_bicycle


class BiCycleTestCase(unittest.TestCase):
    def test_right_hand_rlx(self):
        tags = {'highway': 'residential', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:right': 'lane', 'cycleway:left': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:both': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:left': 'lane', 'cycleway:left:oneway': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:left': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 1))

    def test_right_hand_rmx(self):
        # M1
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'lane', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:right': 'opposite_lane', 'cycleway:left': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # m2a
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:left': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # m2b
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:right': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # m2c
        tags = {'highway': 'residential', 'oneway': 'yes', 'lanes': '2', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # m2d
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway:right': 'lane',
                'cycleway:right:oneway': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # m3a
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway:right': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        # m3b
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway:left': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

    def test_right_hand_rtx(self):
        # t1
        tags = {'highway': 'residential', 'cycleway': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # t2
        tags = {'highway': 'residential', 'cycleway:left': 'track', 'cycleway:left:oneway': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # t3
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:left': 'track', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # t4
        tags = {'highway': 'residential', 'cycleway:left': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 1))

    def test_right_hand_rsx(self):
        # s1
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # s1
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'opposite'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # s2
        tags = {'highway': 'residential', 'cycleway:right': 'track', 'cycleway:left': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 3))

        # s3
        tags = {'highway': 'residential', 'segregated': 'yes', 'cycleway': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # s5
        tags = {'highway': 'path', 'segregated': 'yes', 'foot': 'designated', 'bicycle': 'designated'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

    def test_right_hand_rbx(self):
        # b1
        tags = {'highway': 'residential', 'lanes': '3', 'lanes:forward': '2', 'access:lanes': 'no|yes|yes|no|no',
                'bicycle:lanes': 'designated|yes|yes|designated|yes', 'bus:lanes': 'no|yes|yes|no|designated',
                'taxi:lanes': 'no|yes|yes|no|designated'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # b3
        tags = {'highway': 'residential', 'busway:left': 'lane', 'cycleway:right': 'lane',
                'cycleway:left': 'share_busway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # b4
        tags = {'highway': 'service', 'service': 'bus', 'oneway': 'yes', 'cycleway:left': 'share_busway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # b5
        tags = {'highway': 'residential', 'lanes': '4', 'lanes:bus:forward': '1', 'busway:left': 'lane',
                'cycleway:left': 'share_busway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 1))

        # b6
        tags = {'highway': 'residential', 'cycleway:right': 'share_busway', 'busway': 'opposite_lane', 'oneway': 'yes',
                'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        tags = {'highway': 'residential', 'cycleway:right': 'share_busway', 'busway': 'lane', 'oneway': 'yes',
                'oneway:bus': 'no', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

    def test_right_hand_specials(self):
        # general_oneway
        tags = {'highway': 'cycleway', 'oneway': 'yes'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, False, 3, -1))

        # general
        tags = {'highway': 'cycleway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # cyclestreet
        tags = {'highway': 'residential', 'cyclestreet': 'yes'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # pedestrians_bicycle
        tags = {'highway': 'pedestrian', 'bicycle': 'yes'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # pedestrians
        tags = {'highway': 'pedestrian'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # has_bicycles
        tags = {'highway': 'path'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # nothing
        tags = {'highway': 'residential'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'gbr')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

    def test_left_hand__rlx(self):
        tags = {'highway': 'residential', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:left': 'lane', 'cycleway:right': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:both': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:right': 'lane', 'cycleway:right:oneway': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'cycleway:right': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 1))

    def test_left_hand__rmx(self):
        # M1
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'lane', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:left': 'opposite_lane', 'cycleway:right': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # m2a
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:right': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # m2b
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:left': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # m2c
        tags = {'highway': 'residential', 'oneway': 'yes', 'lanes': '2', 'cycleway': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # m2d
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway:left': 'lane',
                'cycleway:left:oneway': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # m3a
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway:left': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        # m3b
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway:right': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no', 'cycleway': 'opposite_lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

    def test_left_hand__rtx(self):
        # t1
        tags = {'highway': 'residential', 'cycleway': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # t2
        tags = {'highway': 'residential', 'cycleway:right': 'track', 'cycleway:right:oneway': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # t3
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway:right': 'track', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # t4
        tags = {'highway': 'residential', 'cycleway:right': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 1))

    def test_left_hand__rsx(self):
        # s1
        tags = {'highway': 'residential', 'oneway': 'yes', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # s1
        tags = {'highway': 'residential', 'oneway': 'yes', 'cycleway': 'opposite'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # s2
        tags = {'highway': 'residential', 'cycleway:left': 'track', 'cycleway:right': 'lane'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 3))

        # s3
        tags = {'highway': 'residential', 'segregated': 'yes', 'cycleway': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # s5
        tags = {'highway': 'path', 'segregated': 'yes', 'foot': 'designated', 'bicycle': 'designated'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

    def test_left_hand__rbx(self):
        # b1
        tags = {'highway': 'residential', 'lanes': '3', 'lanes:forward': '2', 'access:lanes': 'no|yes|yes|no|no',
                'bicycle:lanes': 'designated|yes|yes|designated|yes', 'bus:lanes': 'no|yes|yes|no|designated',
                'taxi:lanes': 'no|yes|yes|no|designated'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # b3
        tags = {'highway': 'residential', 'busway:right': 'lane', 'cycleway:left': 'lane',
                'cycleway:right': 'share_busway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # b4
        tags = {'highway': 'service', 'service': 'bus', 'oneway': 'yes', 'cycleway:right': 'share_busway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 2, -1))

        # b5
        tags = {'highway': 'residential', 'lanes': '4', 'lanes:bus:forward': '1', 'busway:right': 'lane',
                'cycleway:right': 'share_busway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 1))

        # b6
        tags = {'highway': 'residential', 'cycleway:left': 'share_busway', 'busway': 'opposite_lane', 'oneway': 'yes',
                'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

        tags = {'highway': 'residential', 'cycleway:left': 'share_busway', 'busway': 'lane', 'oneway': 'yes',
                'oneway:bus': 'no', 'oneway:bicycle': 'no'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 2))

    def test_left_hand__specials(self):
        # general_oneway
        tags = {'highway': 'cycleway', 'oneway': 'yes'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, False, 3, -1))

        # general
        tags = {'highway': 'cycleway'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 3, 3))

        # cyclestreet
        tags = {'highway': 'residential', 'cyclestreet': 'yes'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # pedestrians_bicycle
        tags = {'highway': 'pedestrian', 'bicycle': 'yes'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # pedestrians
        tags = {'highway': 'pedestrian'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

        # has_bicycles
        tags = {'highway': 'path'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        tags = {'highway': 'track'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 2, 2))

        # nothing
        tags = {'highway': 'residential'}
        f, b, s_f, s_b = get_bicycle(tags, 3, 'fra')
        self.assertEqual((f, b, s_f, s_b), (True, True, 1, 1))

if __name__ == '__main__':
    unittest.main()
