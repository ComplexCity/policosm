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

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')
from policosm.utils.roads import France


def pedestrianTime(graph):
	pedestrian = {}
	for edge in graph.edges():
		u,v = edge
		length = graph[u][v]['length']
		level = graph[u][v]['level']
		speed = France['speeds'][level]
		
		pedestrianAllowed = True if level < 5 else False
		if pedestrianAllowed:
			pedestrianSpeed = speed if speed <= 5.0 else 5.0
			pedestrian[edge] = length / (pedestrianSpeed* 1000 / 3600.0)
		else:
			pedestrian[edge] = None
	return pedestrian

def motoristTime(graph):
	motorist = {}
	for edge in graph.edges():
		u,v = edge
		length = graph[u][v]['length']
		level = graph[u][v]['level']
		speed = France['speeds'][level]
		
		motoristAllowed = True if level > 1 else False
		if motoristAllowed:
			motorist[edge] = length / (speed * 1000 / 3600.0)
		else:
			motorist[edge] = None
	return motorist

def publicTransportation(graph, publicTransportLevels=[0,1,2,3,4,5,6,7,8]):
	# TODO not implemented yet, sorry (*´ο`*)
	return None


def addTimeTraveltoEdges(graph, transportation=['pedestrian, motorist']):
	print 'motorist in transportation', 'motorist' in transportation
	if 'pedestrian' in transportation:
		nx.set_edge_attributes(graph, 'pedestrian', pedestrianTime(graph))
	if 'motorist' in transportation:
		nx.set_edge_attributes(graph, 'motorist', motoristTime(graph))
	if 'publicTransportation' in transportation:
		nx.set_edge_attributes(graph, 'publicTransportation', motoristTime(graph))

	return graph