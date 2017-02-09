#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	add metric distance between two nodes of an edge
	distance is computed in specified projection system
	to maximize precision

parameters
	graph
	epsg code for targeted projection

how it works
	1 - prepare coordinate projection translation
	2 - for each edge, get source node and target node
	3 - create nodes lines and transform accordingly
	4 - get line length and update metric distance dict
	5 - update whole graph with metric distance dict 

return
	graph with new attribute length on edges
'''

import networkx as nx
import osr, ogr


def addMetricDistanceToEdge(x1,y1,x2,y2, epsgCode):
	# we assume initial epsg is wsg84 (merctor projection)
	
	if epsgCode != 4326:
		sourceProjection = osr.SpatialReference()
		sourceProjection.ImportFromEPSG(4326)
		destinationProjection = osr.SpatialReference()
		destinationProjection.ImportFromEPSG(epsgCode) # https://epsg.io/2154
		coordTrans = osr.CoordinateTransformation(sourceProjection, destinationProjection)
	
	line = ogr.gometry(ogr.wkbLineString)
	line.AddPoint(x1,y1)
	line.AddPoint(x2,y2)
	if epsgCode != 4326:
		line.Transform(coordTrans)
	length = line.Length()

	return length

def addMetricDistanceToEdges(graph, epsgCode):
	# we assume initial epsg is wsg84 (merctor projection)
	metricDistance = {}
	
	if epsgCode != 4326:
		sourceProjection = osr.SpatialReference()
		sourceProjection.ImportFromEPSG(4326)
		destinationProjection = osr.SpatialReference()
		destinationProjection.ImportFromEPSG(epsgCode) # https://epsg.io/2154
		coordTrans = osr.CoordinateTransformation(sourceProjection, destinationProjection)
	
	for edge in graph.edges():
		node1, node2 =  edge
		line = ogr.geometry(ogr.wkbLineString)
		line.AddPoint(graph.node[node1]['longitude'], graph.node[node1]['latitude'])
		line.AddPoint(graph.node[node2]['longitude'], graph.node[node2]['latitude'])
		if epsgCode != 4326:
			line.Transform(coordTrans)
		length = line.Length()
		metricDistance[edge] = length
	nx.set_edge_attributes(graph, 'length', metricDistance)

	return graph