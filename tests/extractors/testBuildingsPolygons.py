#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	extract a graph from 

parameters
	graph

how it works

return
	

'''

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from imposm.parser import OSMParser
import networkx as nx
from policosm.classes.buildings import Buildings

def buildingsPolygons(filename):
	buildings = Buildings()
	osmparser = OSMParser(concurrency=4, coords_callback=buildings.nodes, ways_callback=buildings.osmways, relations_callback=buildings.osmrelations)
	osmparser.parse(filename)
	return buildings.getPolygons()

if __name__ == "__main__":
	polygons = buildingsPolygons('../tests/ajaccio-extract.osm')
	assert len(polygons['features']) == 40

