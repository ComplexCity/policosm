#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in March 2020 in ComplexCity Lab

@author: github.com/fpfaende
"""


import unittest

from shapely.geometry import LineString

from policosm.geoFunctions.linestrings_operation import join_linestrings


class MyTestCase(unittest.TestCase):
    def test_simplify(self):
        line0 = LineString([(0, 0), (1, 1)])
        line1 = LineString([(1, 1), (2, 2)])
        line2 = LineString([(2, 2), (3, 3)])
        lines = []
        self.assertEqual(join_linestrings(lines), None)

        lines = [line0]
        self.assertEqual(join_linestrings(lines), line0)

        lines = [line0, line2]
        self.assertEqual(join_linestrings(lines), None)

        lines = [line0, line1]
        self.assertEqual(join_linestrings(lines), LineString([(0, 0), (1, 1), (2, 2)]))

        lines = [line0, line1, line2]
        self.assertEqual(join_linestrings(lines), LineString([(0, 0), (1, 1), (2, 2), (3, 3)]))

if __name__ == '__main__':
    unittest.main()
