#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in February 2019 in UTSEUS

code for compass bearing comes from astropy
https://docs.astropy.org/en/stable/_modules/astropy/stats/circstats.html#circmean

adapted by github.com/fpfaende
"""
import numpy as np
from more_itertools import pairwise
from shapely.geometry import LineString


def compass_bearing(u: tuple, v: tuple) -> float:
    ux, uy = u
    vx, vy = v
    angle = np.degrees(np.arctan2(vy - uy, vx - ux))
    return (90 - angle) % 360


def _components(data, p=1, phi=0.0, axis=None, weights=None):
    # Utility function for computing the generalized rectangular components
    # of the circular data.
    if weights is None:
        weights = np.ones((1,))
    try:
        weights = np.broadcast_to(weights, data.shape)
    except ValueError:
        raise ValueError('Weights and data have inconsistent shape.')

    C = np.sum(weights * np.cos(p * (data - phi)), axis) / np.sum(weights, axis)
    S = np.sum(weights * np.sin(p * (data - phi)), axis) / np.sum(weights, axis)

    return C, S


def _angle(data, p=1, phi=0.0, axis=None, weights=None):
    # Utility function for computing the generalized sample mean angle
    C, S = _components(data, p, phi, axis, weights)

    # theta will be an angle in the interval [-np.pi, np.pi)
    # [-180, 180)*u.deg in case data is a Quantity
    theta = np.arctan2(S, C)

    return theta


def _length(data, p=1, phi=0.0, axis=None, weights=None):
    # Utility function for computing the generalized sample length
    C, S = _components(data, p, phi, axis, weights)
    return np.hypot(S, C)


def circmean(data, axis=None, weights=None):
    """ Computes the circular mean angle of an array of circular data.

    Parameters
    ----------
    data : numpy.ndarray or Quantity
        Array of circular (directional) data, which is assumed to be in
        radians whenever ``data`` is ``numpy.ndarray``.
    axis : int, optional
        Axis along which circular means are computed. The default is to compute
        the mean of the flattened array.
    weights : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``weights`` represents a
        weighting factor for each group such that ``sum(weights, axis)``
        equals the number of observations. See [1]_, remark 1.4, page 22, for
        detailed explanation.

    Returns
    -------
    circmean : numpy.ndarray or Quantity
        Circular mean.

    References
    ----------
    .. [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
       Series on Multivariate Analysis, Vol. 5, 2001.
    .. [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in
       Circular Statistics (2001)'". 2015.
       <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """
    return _angle(data, 1, 0.0, axis, weights)


def average_compass_bearing_line(line: LineString) -> float:
    """
    Calculates the average weighted bearing for a LineString by
    deconstructing it into segment where bearing is the segment oriented angle and
    weight is the length of the segment.

    :Parameters:
      - `line: LineString in meter projection
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """

    coords = list(line.coords)
    bearings = []
    amounts = []
    for u, v in pairwise(coords):
        bearing = compass_bearing(u, v)
        bearings.append(bearing)
        amount = LineString([u, v]).length
        amounts.append(amount)

    if len(bearings) == 1:
        return bearings[0]
    else:
        return np.degrees(circmean(np.radians(bearings), weights=amounts)) % 360
