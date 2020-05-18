#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in March 2020 in ComplexCity Lab

@author: github.com/fpfaende
"""

import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


def join_linestrings(linestrings: list) -> LineString:
    r"""
    Simplify a list of n LineString [LineString a, ...,LineString n].
    if the list is empty, function returns None
    if the list had one element, it returns this element
    if the list has several segments but disjoint function returns None
    otherwise it create a new linestring from the successive segments

    Returns
    -------
    LineString
      a LineString joining all LineString segments
    """

    if len(linestrings) == 0:
        return None
    elif len(linestrings) == 1:
        return linestrings[0]

    simple_line = []
    for i in range(len(linestrings) - 1):
        if linestrings[i].coords[-1] != linestrings[i + 1].coords[0]:
            return None
        simple_line += list(linestrings[i].coords[:-1])
    simple_line += list(linestrings[i + 1].coords)

    return LineString(simple_line)


def cut_linestring(line: LineString, distance: float) -> list:
    r"""
    Cuts a line in two at a distance from its starting point
    courtesy of shapely doc

    Parameters
    ----------
    :param line : LineString to cut
    :param distance : float distance to cut

    Returns
    -------
    LineString : list
       list of LineString
    """

    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [LineString(coords[:i + 1]), LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [LineString(coords[:i] + [(cp.x, cp.y)]), LineString([(cp.x, cp.y)] + coords[i:])]


def asymmetric_segment_buffer(a: Point, b: Point, a_buffer: float, b_buffer: float) -> Polygon:
    r"""
    create an asymmetric polygonal buffer around a segment a––b

    Parameters
    ----------
    :param a : shapely Point
    :param b : shapely Point
    :param a_buffer : float, buffered value around a
    :param b_buffer : float, buffered value around b

    Returns
    -------
    Polygon :
       buffered segment
    """

    if a_buffer > 0:
        a = a.buffer(a_buffer)
        a = np.ravel(np.array(a.exterior.coords.xy), order='F')
    else:
        a = np.ravel(np.array(a.xy), order='F')

    if b_buffer > 0:
        b = b.buffer(b_buffer)
        b = np.ravel(np.array(b.exterior.coords.xy), order='F')
    else:
        b = np.ravel(np.array(b.xy), order='F')

    h = np.concatenate((a, b), axis=None)
    h = np.reshape(h, (-1, 2))

    hull = ConvexHull(h)
    xs, ys = h[hull.vertices, 0], h[hull.vertices, 1]
    return Polygon(zip(xs, ys))


def asymmetric_line_buffer(line: LineString, start_value: float, end_value: float) -> Polygon:
    r"""
    create an asymmetric polygonal buffer around a line made of one or more segment a––•––•–––––b
    it splits the line into segments, interpolate the buffers value between start and end and make a union of polygons around it

    Parameters
    ----------
    :param line: a LineString
    :param start_value: a float representing distance from start of the line
    :param end_value: a float representing distance from end of the line

    Returns
    -------
    Polygon :
       unionized asymmetric buffered segments of a line
    """

    if start_value == end_value:
        return line.buffer(start_value)

    coords = list(line.coords)
    dists = [0] + [LineString(line.coords[:i + 1]).length for i in range(1, len(coords) - 1)] + [line.length]
    buffers = np.interp(dists, [0, line.length], [start_value, end_value])

    polygons = []
    for i in range(len(coords) - 1):
        polygons.append(asymmetric_segment_buffer(Point(coords[i]), Point(coords[i + 1]), buffers[i], buffers[i + 1]))
    return unary_union(polygons)
