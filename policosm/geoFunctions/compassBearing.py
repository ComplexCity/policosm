#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in February 2019 in UTSEUS

@author: github.com/jeromer
from https://gist.github.com/jeromer/2005586
adapted by github.com/fpfaende
"""
import math


def compass_bearing(u, v):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(u) != tuple) or (type(v) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(u[0])
    lat2 = math.radians(v[0])

    difference_longitude = math.radians(v[1] - u[1])

    x = math.sin(difference_longitude) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                           * math.cos(lat2) * math.cos(difference_longitude))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360

    return bearing
