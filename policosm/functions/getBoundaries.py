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

import geojson
import networkx as nx

def getRoadsBoundaries(graph):
	lons = nx.get_node_attributes(graph,'longitude').values()
	lats = nx.get_node_attributes(graph,'latitude').values()
	
	lon = lons[0]
	lat = lats[0]
	
	bounds = [lon,lat,lon,lat]
	
	for i in range(0,len(lons)):
		lon = lons[i]
		lat = lats[i]
		if lon < bounds[0]:
			bounds[0] = lon
		if lon > bounds[2]:
			bounds[2] = lon
		if lat < bounds[1]:
			bounds[1] = lat
		if lat > bounds[3]:
			bounds[3] = lat
	return bounds

def getBuildingsBoundaries(polygons):
	lons = []
	lats = []

	for polygons in polygons['features']:
		for x,y in polygons['geometry']['coordinates'][0]:
			lons.append(x)
			lats.append(y)
	
	lon = lons[0]
	lat = lats[0]
	
	bounds = [lon,lat,lon,lat]
	
	for i in range(0,len(lons)):
		lon = lons[i]
		lat = lats[i]
		if lon < bounds[0]:
			bounds[0] = lon
		if lon > bounds[2]:
			bounds[2] = lon
		if lat < bounds[1]:
			bounds[1] = lat
		if lat > bounds[3]:
			bounds[3] = lat
	return bounds

if __name__ == "__main__":
	testGraph = nx.Graph()
	testGraph.add_node(1,longitude=1.0, latitude=1.0)
	testGraph.add_node(2,longitude=2.0, latitude=2.0)
	testGraph.add_edge(1, 2,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	print getRoadsBoundaries(testGraph)

	dump = '{"features": [{"geometry":{"coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]], "type": "Polygon"},"type": "Feature"}]}'
	polygons = geojson.loads(dump)
	print getBuildingsBoundaries(polygons)

