#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in June 2016 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	define integer roads levels according to highway tag in open street map
'''

levels = {'levels':[
	{0: ['construction', 'demolished', 'raceway', 'abandoned', 'disused', 'foo', 'no']},
	{1: ['stairway','elevator', 'corridor', 'escape']},
	{2: ['services', 'access','via_ferrata','access_ramp', 'emergency_access_point', 'service','footway', 'traffic_island','virtual','cyleway', 'cycleway','byway','path', 'track','living_street', 'pedestrian', 'steps', 'platform', 'bridleway', 'rest_area', 'escape']},
	{3: ['residential', 'yes', 'bus_guideway', 'bus_stop', 'unclassified', 'road', 'crossing', 'unknown', 'proposed', 'bridge', 'lane', 'ford','psv']},
	{4: ['tertiary', 'tertiary_link', 'turning_circle']},
	{5: ['secondary', 'secondary_link']},
	{6: ['primary', 'primary_link' ]},
	{7: ['trunk', 'trunk_link']},
	{8: ['motorway', 'motorway_link']}
	]
}