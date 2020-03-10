#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in June 2016 in ComplexCity Lab

@author: github.com/fpfaende

what it does
define integer roads levels according to highway tag in open street map
define average speeds for levels in cities. TODO A precise study shall make it better (tomtom traffic for example)
see wikipedia https://en.wikipedia.org/wiki/Preferred_walking_speed

"""

import logging
logging.getLogger().setLevel(logging.INFO)


def get_level(highway):
    try:
        return levels[highway]
    except KeyError:
        logging.warning('level not found for tag highway – {0}, default to 3'.format(highway))
        return 3


levels_readable = {'levels': [
    {0: ['construction', 'demolished', 'raceway', 'abandoned', 'disused', 'foo', 'no','projected', 'planned','proposed','razed','dismantled','historic']},
    {1: ['stairway', 'stairs',  'elevator', 'corridor', 'hallway', 'slide']},
    {2: ['services', 'bus', 'busway', 'bus_guideway', 'access', 'bus_stop', 'via_ferrata', 'access_ramp', 'emergency_access_point', 'emergency_bay','service', 'footway',
         'traffic_island', 'virtual', 'cyleway', 'cycleway', 'byway', 'path', 'track', 'pedestrian', 'steps',
         'platform', 'bridleway', 'rest_area', 'escape', 'footway']
     },
    {3: ['residential', 'yes', 'unclassified', 'crossing', 'unknown',
         'bridge', 'lane', 'ford', 'psv', 'living_street','alley']
     },
    {4: ['tertiary', 'tertiary_link', 'turning_circle', 'road', 'roundabout', 'ice_road']},
    {5: ['secondary', 'secondary_link']},
    {6: ['primary', 'primary_link']},
    {7: ['trunk', 'trunk_link']},
    {8: ['motorway', 'motorway_link','ramp']}
], 'public_transport': [
    {0: 'Buses'},  # PSV lanes, busway, bus guideway, routes, stops, platform, stations
    {1: 'Trolleybuses'},  # Routes, wires, stops
    {2: 'Trains'},  # Tracks, railway routes, train routes, halt, stations
    {3: 'Light rail'},  # Tracks, routes, stations
    {4: 'Metros'},  # Tracks, routes, stations, entrances
    {5: 'Trams'},  # Tracks, routes, stops
    {6: 'Aerialways'},  # cable car, gondola, chair lift, drag lift, zip line, stations, pylons
    {7: 'Ferries'},  # Shipping lanes, routes, ports, docks
    {8: 'Flights'}  # Runways, taxiways, aprons, terminals, aerodromes, hangars, heliports, helipads
]
}

levels = {}
for level_dict in levels_readable['levels']:
    for level, highway_tags in level_dict.items():
        for highway_tag in highway_tags:
            levels[highway_tag] = level

# see speed observatory for France ONISR
France = {'speeds': {
    0: 3.0,
    1: 4.0,
    2: 5.0,
    3: 30.0,
    4: 40.0,
    5: 50.0,
    6: 70.0,
    7: 81.0,
    8: 110.0
}
}
