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

from rtree import index
import geojson

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

		linestring = geojson.LineString([(x1, y1), (x2, y2)])
		feature = geojson.Feature(geometry=linestring, properties={"node1": node1 ,"node2": node2},id=data['osmid']) 

		if interleaved:
			yield (i, (minx, miny, maxx, maxy), geojson.dumps(feature, sort_keys=True))
		else:
			yield (i, (minx, maxx, miny, maxy), geojson.dumps(feature, sort_keys=True))

def nodesGenerator(graph, interleaved=True):
	nodes = graph.nodes(data=True)
	
	for i, (node, data) in enumerate(nodes):
		x = data['longitude']
		y = data['latitude']

		point = geojson.Point([x,y])
		feature = geojson.Feature(geometry=point,id=node)

		if interleaved:
			yield (i, (x, y, x, y), geojson.dumps(feature, sort_keys=True))
		else:
			yield (i, (x, x, y, y), geojson.dumps(feature, sort_keys=True))

def getGraphRtree(graph, generator='edges', filename=None, interleaved=True):
	p = index.Property()
	p.overwrite = True

	if filename is None:
		if generator == 'edges':
			return index.Rtree(edgesGenerator(graph,interleaved), properties = p, interleaved=interleaved)
		elif generator == 'nodes':
			return index.Rtree(nodesGenerator(graph,interleaved), properties = p, interleaved=interleaved)
	else:
		return index.Rtree(filename, interleaved)
