#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString

from policosm.geoNetworks.simplify import simplify_directed_as_dataframe, simplify_undirected_as_dataframe


def make_a_dataframe(etuples):
    df = pd.DataFrame.from_records(etuples, index='osm_id',
                                   columns=['osm_id', 'u', 'v', 'highway', 'one_way', 'level', 'lanes',
                                            'width', 'bicycle', 'bicycle_safety',
                                            'foot', 'foot_safety', 'max_speed', 'motorcar', 'geometry'])
    return gpd.GeoDataFrame(df, geometry='geometry', crs=1)


class SimplifyDirectedTestCase(unittest.TestCase):
    def setUp(self):
        self.attributes = [True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(0, 0), (1, 1)])]

    def test_degree_4_no_loop(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 2, 'a') + tuple(self.attributes), ('0', 2, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)
        np.testing.assert_equal(np.array([4, 3, 2, 1]), e2)

    def test_degree_4_no_loop_line(self):
        edge_tuples = [
            ('0', 1, 2, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(0, 0), (1, 0)])]),
            ('0', 2, 3, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(1, 0), (2, 0)])]),
            ('0', 3, 4, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(2, 0), (3, 0)])]),
            ('0', 4, 3, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(3, 0), (2, 0)])]),
            ('0', 3, 2, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(2, 0), (1, 0)])]),
            ('0', 2, 1, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(1, 0), (0, 0)])])]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)
        np.testing.assert_equal(np.array([4, 3, 2, 1]), e2)
        l1, l2 = df.geometry.to_list()
        self.assertEquals(l1, LineString([(0, 0), (1, 0), (2, 0), (3, 0)]))
        self.assertEquals(l2, LineString([(3, 0), (2, 0), (1, 0), (0, 0)]))

    def test_degree_4_loop(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 2, 'a') + tuple(self.attributes), ('0', 2, 1, 'a') + tuple(self.attributes),
                       ('0', 1, 4, 'a') + tuple(self.attributes), ('0', 4, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([3, 2, 1, 4]), e1)
        np.testing.assert_equal(np.array([4, 1, 2, 3]), e2)

    def test_degree_4_no_loop_change_highway(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 3, 'b') + tuple(self.attributes),
                       ('0', 3, 2, 'a') + tuple(self.attributes), ('0', 2, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2, e3, e4 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3]), e1)
        np.testing.assert_equal(np.array([3, 4]), e2)
        np.testing.assert_equal(np.array([3, 2, 1]), e3)
        np.testing.assert_equal(np.array([4, 3]), e4)

    def test_degree_4_loop_change_highway(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, '') + tuple(self.attributes), ('0', 4, 3, 'b') + tuple(self.attributes),
                       ('0', 3, 2, 'a') + tuple(self.attributes), ('0', 2, 1, 'a') + tuple(self.attributes),
                       ('0', 1, 4, 'a') + tuple(self.attributes), ('0', 4, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2, e3, e4 = df.path.to_list()
        np.testing.assert_equal(np.array([3, 4]), e1)
        np.testing.assert_equal(np.array([3, 2, 1, 4]), e2)
        np.testing.assert_equal(np.array([4, 3]), e3)
        np.testing.assert_equal(np.array([4, 1, 2, 3]), e4)

    def test_degree_4_no_loop_looooooong(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 5, 'a') + tuple(self.attributes),
                       ('0', 5, 6, 'a') + tuple(self.attributes), ('0', 6, 7, 'a') + tuple(self.attributes),
                       ('0', 7, 8, 'a') + tuple(self.attributes), ('0', 8, 7, 'a') + tuple(self.attributes),
                       ('0', 7, 6, 'a') + tuple(self.attributes), ('0', 6, 5, 'a') + tuple(self.attributes),
                       ('0', 5, 4, 'a') + tuple(self.attributes), ('0', 4, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 2, 'a') + tuple(self.attributes), ('0', 2, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4, 5, 6, 7, 8]), e1)
        np.testing.assert_equal(np.array([8, 7, 6, 5, 4, 3, 2, 1]), e2)

    def test_degree_2_no_loop(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)

    def test_degree_2_loop(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, = df.path.to_list()
        np.testing.assert_equal(np.array([3, 4, 1, 2]), e1)

    def test_degree_2_no_loop_change_highway(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'b') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3]), e1)
        np.testing.assert_equal(np.array([3, 4]), e2)

    def test_degree_2_loop_change_highway(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 1, 'b') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)
        np.testing.assert_equal(np.array([4, 1]), e2)

    def test_degree_2_no_loop_looooooong(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 5, 'a') + tuple(self.attributes),
                       ('0', 5, 6, 'a') + tuple(self.attributes), ('0', 6, 7, 'a') + tuple(self.attributes),
                       ('0', 7, 8, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)
        e1, = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4, 5, 6, 7, 8]), e1)

    def test_complicated(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 5, 'p') + tuple(self.attributes),
                       ('0', 5, 6, 'r') + tuple(self.attributes), ('0', 6, 7, 'r') + tuple(self.attributes),
                       ('0', 7, 5, 'r') + tuple(self.attributes), ('0', 4, 8, 'f') + tuple(self.attributes),
                       ('0', 8, 9, 'f') + tuple(self.attributes), ('0', 9, 1, 'f') + tuple(self.attributes),
                       ('0', 1, 9, 'b') + tuple(self.attributes), ('0', 9, 8, 'b') + tuple(self.attributes),
                       ('0', 8, 4, 'b') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_directed_as_dataframe(df)

        e1, e2, e3, e4, e5 = df.path.to_list()
        h1, h2, h3, h4, h5 = df.highway.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e2)
        np.testing.assert_equal(np.array([1, 9, 8, 4]), e1)
        np.testing.assert_equal(np.array([4, 8, 9, 1]), e4)
        np.testing.assert_equal(np.array([4, 5]), e3)
        np.testing.assert_equal(np.array([5, 6, 7, 5]), e5)
        self.assertEquals('b', h1)
        self.assertEquals('a', h2)
        self.assertEquals('p', h3)
        self.assertEquals('f', h4)
        self.assertEquals('r', h5)


class SimplifyUndirectedTestCase(unittest.TestCase):
    def setUp(self):
        self.attributes = [True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(0, 0), (1, 1)])]

    def test_no_loop(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_undirected_as_dataframe(df)
        e1, = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)
        self.assertEqual(1, df.iloc[0].u)
        self.assertEqual(4, df.iloc[0].v)

    def test_no_loop_line(self):
        edge_tuples = [
            ('0', 1, 2, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(0, 0), (1, 0)])]),
            ('0', 2, 3, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(1, 0), (2, 0)])]),
            ('0', 3, 4, 'a') + tuple([True, 3, 2, 2.0, True, 0, True, 0, 30, True, LineString([(2, 0), (3, 0)])])]

        df = make_a_dataframe(edge_tuples)
        df = simplify_undirected_as_dataframe(df)
        e1, = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)

        l1, = df.geometry.to_list()
        print(df.geometry)
        self.assertEquals(l1, LineString([ (0, 0), (1, 0), (2, 0), (3, 0)]))

    def test_loop(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_undirected_as_dataframe(df)
        e1, = df.path.to_list()
        np.testing.assert_equal(np.array([4, 1, 2, 3]), e1)

    def test_no_loop_change_highway(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'b') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_undirected_as_dataframe(df)
        e1, e2, e3 = df.path.to_list()
        np.testing.assert_equal(np.array([1, 2]), e1)
        np.testing.assert_equal(np.array([2, 3]), e2)
        np.testing.assert_equal(np.array([3, 4]), e3)

    def test_loop_change_highway(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, '') + tuple(self.attributes), ('0', 4, 1, 'a') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_undirected_as_dataframe(df)
        e1, e2 = df.path.to_list()
        np.testing.assert_equal(np.array([4, 1, 2, 3]), e2)
        np.testing.assert_equal(np.array([3, 4]), e1)

    def test_complicated(self):
        edge_tuples = [('0', 1, 2, 'a') + tuple(self.attributes), ('0', 2, 3, 'a') + tuple(self.attributes),
                       ('0', 3, 4, 'a') + tuple(self.attributes), ('0', 4, 5, 'p') + tuple(self.attributes),
                       ('0', 5, 6, 'r') + tuple(self.attributes), ('0', 6, 7, 'r') + tuple(self.attributes),
                       ('0', 7, 5, 'r') + tuple(self.attributes), ('0', 4, 8, 'f') + tuple(self.attributes),
                       ('0', 8, 9, 'f') + tuple(self.attributes), ('0', 9, 1, 'f') + tuple(self.attributes)]

        df = make_a_dataframe(edge_tuples)
        df = simplify_undirected_as_dataframe(df)

        e1, e2, e3, e4 = df.path.to_list()
        h1, h2, h3, h4 = df.highway.to_list()
        np.testing.assert_equal(np.array([1, 2, 3, 4]), e1)
        np.testing.assert_equal(np.array([4, 5]), e2)
        np.testing.assert_equal(np.array([4, 8, 9, 1]), e3)
        np.testing.assert_equal(np.array([5, 6, 7, 5]), e4)

        self.assertEquals('a', h1)
        self.assertEquals('p', h2)
        self.assertEquals('f', h3)
        self.assertEquals('r', h4)



if __name__ == '__main__':
    unittest.main()
