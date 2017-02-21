#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	remove nodes from osm road graph outside of the bounding box

parameters
	graph
	array of 4 coordinates [lon1,lat1,lon2,lat2]

how it works
	remove nodes outside of bounding box 

	lon1,lat1———————————+
		|	o		o	|	x
	x	|		o		|	
		+———————————lon2,lat2
			x
return
	graph minus nodes outside of bounding box
'''

import networkx as nx

def boundingBox(graph, coordinates):
	minlon = min(coordinates[0], coordinates[2])
	maxlon = max(coordinates[0], coordinates[2])
	minlat = min(coordinates[1], coordinates[3])
	maxlat = max(coordinates[1], coordinates[3])

	for node in graph.nodes():
		if 'latitude' not in graph.node[node]:
			graph.remove_node(node)
			continue
		if graph.node[node]['longitude'] < minlon:
			graph.remove_node(node)
			continue
		if graph.node[node]['longitude'] > maxlon:
			graph.remove_node(node)
			continue
		if graph.node[node]['latitude'] < minlat:
			graph.remove_node(node)
			continue
		if graph.node[node]['latitude'] > maxlat:
			graph.remove_node(node)
			continue
	return graph