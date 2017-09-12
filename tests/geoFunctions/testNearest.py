#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does

graph

how it works

return


'''

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from shapely.geometry import Point

def nearestNode(source, candidates):
	nearestNode = {}
	for key, point in candidates.iteritems():
		nearestNode[source.distance(point)] = key
	return min(nearestNode.keys()), nearestNode[min(nearestNode.keys())]