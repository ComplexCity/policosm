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

import networkx as nx
from shapely.geometry import Polygon, LineString


def getCentroidsFromRoadsGraph(graph):
	lines = []
	for u,v in graph.edges():
		ucoo = (graph.node[u]['longitude'], graph.node[u]['latitude'])
		vcoo = (graph.node[v]['longitude'], graph.node[v]['latitude'])
		line = LineString([ucoo,vcoo])
		x = line.centroid.x
		y = line.centroid.y
		lines.append((x,y))
	return lines


def getCentroidFromRoadsGraph(graph):
	lines = getCentroidsFromRoadsGraph(graph)
	x=0
	y=0
	for xc, yc in lines:
		x += xc
		y += yc
	x = x / float(len(lines))
	y = y / float(len(lines))
	return (x,y)

if __name__ == "__main__":
	testGraph = nx.Graph()
	testGraph.add_node(1,longitude=1.0, latitude=1.0)
	testGraph.add_node(2,longitude=2.0, latitude=2.0)
	testGraph.add_edge(1, 2,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	assert getCentroidFromRoadsGraph(testGraph) == (1.5,1.5)