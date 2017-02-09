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
from rtree import index
from rtree.index import Rtree
import geojson
from geojson import Feature, LineString


def edgesGenerator(graph, interleaved=True):
	edges = graph.edges(data=True)

	for i, (node1, node2, data) in enumerate(edges):
		x1 = graph.node[node1]['longitude']
		x2 = graph.node[node2]['longitude']
		y1 = graph.node[node1]['latitude']
		y2 = graph.node[node2]['latitude']

		minx = min([x1,x2])
		maxx = max([x1,x2])
		miny = min([y1,y2])
		maxy = max([y1,y2])

		linestring = LineString([(x1, y1), (x2, y2)])
		feature = Feature(geometry=linestring, properties={"node1": node1 ,"node2": node2},id=data['osmid']) 

		if interleaved:
			yield (i, (minx, miny, maxx, maxy), geojson.dumps(feature, sort_keys=True))
		else:
			yield (i, (minx, maxx, miny, maxy), geojson.dumps(feature, sort_keys=True))

def getRtree(graph,filename=None, interleaved=True):
	p = index.Property()
	p.overwrite = True

	if filename is None:
		return index.Rtree(edgesGenerator(graph,True), properties = p, interleaved=True)
	else:
		return index.Rtree(filename, interleaved=True)
