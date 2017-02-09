#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
extract a graph from 

	o       			      O 
               becomes		  |
o——————————o 			o—————o————o

parameters
graph

how it works

return
Careful, this graph is not an osm compatible graph as new roads were artificially created
Algorithm based on osmid will perform with unpredictable results

'''

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')
from policosm.functions.getRtree import getRtree
from policosm.geo_networks.addMetricDistanceToEdges import addMetricDistanceToEdge

import networkx as nx
import json
from shapely.geometry import Polygon, LineString, Point


def linkNewNodes(graph, nodes, rtreeFilename=None, epsgCode=4326, level=2, highway='path'):
	r = getRtree(graph,rtreeFilename,True)

	for newid, lon, lat in nodes:
		z = Point(lon,lat)

		if newid is None:
			newid = z.wkt # if newid undefined, create hashable object

		# get the closest edge from the node
		hits = r.nearest((z.x, z.y, z.x,z.y), 1, objects="raw")
		nearestJson = json.loads(list(hits)[0])
		
		# find the coordinates of the connection node on the existing edge
		u, v = nearestJson['properties'].values()
		ucoo = (graph.node[u]['longitude'], graph.node[u]['latitude'])
		vcoo = (graph.node[v]['longitude'], graph.node[v]['latitude'])
		line = LineString([ucoo,vcoo])
		lineLength = line.length
		segmentLength = line.project(z)
		x,y = line.interpolate(segmentLength).coords[0]
		w = Point(x,y)
		
		# recreate graph structure
		attributes = graph[u][v]
		uwAttributes = attributes
		wvAttributes = attributes

		if 'length' in attributes:
			realLength = graph[u][v]['length']
			uwLength = segmentLength * realLength / lineLength
			wvLength = (lineLength - segmentLength) * realLength / lineLength

			uwAttributes['length'] = uwLength
			wvAttributes['length'] = wvLength
		
		graph.add_node(w.wkt,longitude=w.x, latitude=w.y)
		graph.add_edge(u,w.wkt, uwAttributes)
		graph.add_edge(w.wkt,v, wvAttributes)
		graph.remove_edge(u,v)
 
		attributes['level'] = level
		attributes['highway'] = highway
		attributes['osmid'] = '-1'
		if 'length' in attributes:
			attributes['length'] = addMetricDistanceToEdge(z.x, z.y, w.x, w.y, epsgCode)

		graph.add_node(newid, longitude=lon, latitude=lat)
		graph.add_edge(newid, w.wkt, attributes)

	return graph
		

if __name__ == "__main__":
	testGraph = nx.Graph()
	testGraph.add_node(1,longitude=1.0, latitude=1.0)
	testGraph.add_node(2,longitude=2.0, latitude=1.0)
	testGraph.add_node(3,longitude=3.0, latitude=3.0)
	testGraph.add_edge(1, 2,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	testGraph.add_edge(2, 3,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	newNode1 = (None, 1.2, 1.8)
	newNode2 = (None, 2.8, 2.2)
	import matplotlib.pyplot as plt
	
	G = linkNewNodes(testGraph, [newNode1, newNode2])
	

	eoriginal=[(u,v) for (u,v,d) in G.edges(data=True) if d['level'] == 3]
	enew=[(u,v) for (u,v,d) in G.edges(data=True) if d['level'] == 2]

	pos={}
	for n in G.nodes():
		pos[n] = (G.node[n]['longitude'],G.node[n]['latitude'])

	# nodes
	nx.draw_networkx_nodes(G,pos,node_size=3)

	# edges
	nx.draw_networkx_edges(G,pos,edgelist=eoriginal,width=2)
	nx.draw_networkx_edges(G,pos,edgelist=enew,width=2,alpha=0.5,edge_color='r')

	# labels
	nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

	plt.show()



