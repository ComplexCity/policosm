#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
extract a graph from 

	o   o    			      o  o  
               becomes		  |  |
o——————————o 			o—————o——o—o

parameters
graph

how it works

return
Careful, this graph is not an osm compatible graph as new roads were artificially created
Algorithm based on osmid will perform with unpredictable results

'''

import itertools
import json

import networkx as nx
from shapely.geometry import Point

from policosm.functions.getRtree import *
from policosm.geoFunctions.nearest import nearestNode


#TODO add length attribute test to connect graph

def connectGraphComponents(graph, level=2, highway='path', connectNearest=False):
	if nx.is_connected(graph):
		return graph

	combinations = itertools.permutations(range(nx.number_connected_components(graph)),2)

	subgraphs = list(nx.connected_component_subgraphs(graph, copy=True))
	rtrees = [getGraphRtree(subgraph,'nodes') for subgraph in subgraphs]

	nearestComponents={}
	for i, j in combinations:
		if i not in nearestComponents:
			nearestComponents[i] = []
		smallest = i if len(subgraphs[i]) < len(subgraphs[j]) else j
		biggest = j if smallest is i else i
		candidates = {}
		nearestNeighbors = {}
		
		for node1, data in subgraphs[smallest].nodes(data=True):
			x, y = data['longitude'], data['latitude']
			hits = list(rtrees[biggest].nearest((x, y, x, y), 2, objects="raw"))
			for candidate in hits:
				data = json.loads(candidate)
				candidates[data['id']] = Point(data['geometry']['coordinates'])
			source = Point([x,y])
			distance, node2 = nearestNode(source, candidates)
			nearestNeighbors[distance] = node1, node2
			u,v = nearestNeighbors[min(nearestNeighbors.keys())]
		
		if connectNearest:
			nearestComponents[i].append((j, min(nearestNeighbors.keys()), (u,v)))
		else:
			newAttributes = {'level':level, 'highway': highway,'osmid':'-1','policosm':True, 'lanes':1,'oneway': False}
			graph.add_edge(u, v, newAttributes)

	if connectNearest:
		for i in nearestComponents.keys():
			data = nearestComponents[i]
			j, distance, (u,v) = sorted(data, key=lambda tup: tup[1])[0]

			if not graph.has_edge(u, v):
				newAttributes = {'level':level, 'highway': highway,'osmid':'-1','policosm':True, 'lanes':1,'oneway': False}
				graph.add_edge(u, v, newAttributes)
	return connectGraphComponents(graph, level, highway, connectNearest=connectNearest)


if __name__ == "__main__":
	testGraph = nx.Graph()
	testGraph.add_node(1,longitude=0.0, latitude=1.0)
	testGraph.add_node(2,longitude=1.0, latitude=1.0)
	testGraph.add_node(3,longitude=1.0, latitude=2.0)
	testGraph.add_node(4,longitude=2.0, latitude=1.0)
	testGraph.add_node(5,longitude=1.0, latitude=0.0)
	
	testGraph.add_node(6,longitude=3.0, latitude=2.0)
	testGraph.add_node(7,longitude=4.0, latitude=1.0)
	testGraph.add_node(8,longitude=5.0, latitude=2.0)
	testGraph.add_node(9,longitude=3.0, latitude=0.0)
	testGraph.add_node(10,longitude=5.0, latitude=0.0)

	testGraph.add_node(11,longitude=2.0, latitude=3.0)

	testGraph.add_node(12,longitude=2.5, latitude=1.2)

	# testGraph.add_edge(2, 1,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	# testGraph.add_edge(2, 3,osmid=4,highway='residential',level=3, lanes=1, oneway=False)
	# testGraph.add_edge(2, 4,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	# testGraph.add_edge(2, 5,osmid=3,highway='residential',level=3, lanes=1, oneway=False)

	# testGraph.add_edge(7, 6,osmid=4,highway='residential',level=3, lanes=1, oneway=False)
	# testGraph.add_edge(7, 8,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	# testGraph.add_edge(7, 9,osmid=4,highway='residential',level=3, lanes=1, oneway=False)
	# testGraph.add_edge(7, 10,osmid=3,highway='residential',level=3, lanes=1, oneway=False)

	print (nx.is_connected(testGraph))
	testGraph = connectGraphComponents(testGraph, connectNearest=True)
	print (nx.is_connected(testGraph))
	
	pos={}
	labels = {}

	for n in testGraph.nodes():
		labels[n] = n
		pos[n] = (testGraph.node[n]['longitude'],testGraph.node[n]['latitude'])

	nx.draw_networkx_nodes(testGraph,pos,node_size=1,alpha=0.1,color='b')
	nx.draw_networkx_edges(testGraph,pos,edgelist=testGraph.edges(),width=1,edge_color='r')
	nx.draw_networkx_labels(testGraph,pos,labels=labels, font_size=16, font_color='k', font_family='sans-serif', alpha=1.0)
	plt.show()
