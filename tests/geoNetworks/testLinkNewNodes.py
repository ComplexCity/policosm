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

import hashlib
import networkx as nx
import json
from shapely.geometry import Polygon, LineString, Point, shape

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from policosm.functions.getRtree import *
from policosm.geoNetworks.addMetricDistanceToEdges import addMetricDistanceToEdge

def nearestEdgeFromPoint(candidates, point):
	nearestCouple = {}
	for candidate in candidates:
		line = json.loads(candidate)
		point.distance(LineString(line['geometry']['coordinates']))
		
		nearestCouple[point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
	mindistance = min(nearestCouple.keys())
	return nearestCouple[mindistance]

def distance(graph, source, target):
	point = Point((graph.node[source]['longitude'], graph.node[source]['latitude']))
	return point.distance(Point((graph.node[target]['longitude'], graph.node[target]['latitude'])))

def getKey(item):
    return item[1]

def nearestNode(graph, source, candidates):
	point = Point((graph.node[source]['longitude'], graph.node[source]['latitude']))
	nearestNode = {}
	for candidate in candidates:
		nearestNode[point.distance(Point((graph.node[candidate]['longitude'], graph.node[candidate]['latitude'])))] = candidate
	mindistance = min(nearestNode.keys())
	return nearestNode[mindistance]

def linkNewNodes(graph, nodes, rtreeFilename=None, epsgCode=4326, level=2, highway='path', threshold=0.0):
	r = getGraphRtree(graph,generator='edges',filename=rtreeFilename,interleaved=True)
	modifiedEdges = set()
	newNodes = set()

	for lon, lat in nodes:
		z = Point(lon,lat)

		# create a new integer as id for the new node z we try to add
		zid = -int(hashlib.md5(z.wkt).hexdigest(), 16) 

		# get the closest edge from the new node to wire it to it 
		hits = r.nearest((z.x, z.y, z.x,z.y), 3, objects="raw")
		u,v =  nearestEdgeFromPoint(list(hits), z)

		# we got the nearest edge source and target
		# if the projection of the new node z is inside the segment ([–o——] and not o [–———])
		# 		we create a new node w on the edge and redistribute length
		ucoo = (graph.node[u]['longitude'], graph.node[u]['latitude'])
		vcoo = (graph.node[v]['longitude'], graph.node[v]['latitude'])
		line = LineString([ucoo,vcoo])
		lineLength = line.length
		segmentLength = line.project(z)

		if segmentLength == 0:
			wid = u
			w = Point(ucoo[0],ucoo[1])
		elif segmentLength == lineLength:
			wid = v
			w = Point(vcoo[0],vcoo[1])
		else:
			x,y = line.interpolate(segmentLength).coords[0]
			w = Point(x,y)
			wid  = -int(hashlib.md5(w.wkt).hexdigest(), 16)
			newNodes.add(wid)

			attributes = graph[u][v]
			uwAttributes = attributes.copy()
			wvAttributes = attributes.copy()

			if 'length' in attributes:
				uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
				wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
			
			uwAttributes['policosm'] = True
			wvAttributes['policosm'] = True
			
			graph.add_node(wid,longitude=w.x, latitude=w.y)
			graph.add_edge(u,wid, uwAttributes)
			graph.add_edge(wid,v, wvAttributes)
			
			# add to the set for future rewiring 
			# making sure it is unique one way of the other (uv, vu)
			if u < v:
				modifiedEdges.add((u,v))
			else:
				modifiedEdges.add((v,u))
 		
 		newAttributes = {}
		newAttributes['level'] = level
		newAttributes['highway'] = highway
		newAttributes['osmid'] = '-1'
		newAttributes['policosm'] = True
		newAttributes['lanes'] = 1
		newAttributes['oneway'] = False
		newAttributes['policosm'] = True
		if 'length' in graph[u][v]:
			newAttributes['length'] = addMetricDistanceToEdge(z.x, z.y, w.x, w.y, epsgCode)

		graph.add_node(zid, longitude=lon, latitude=lat)
		graph.add_edge(zid, wid, newAttributes)

	for u,v in modifiedEdges:
		paths = nx.all_simple_paths(graph, source=u, target=v, cutoff=2)
		
		nodes = set()
		previousNode = u
		deleteUNodes = []
		deleteVNodes = []
		paths = nx.all_simple_paths(graph, source=u, target=v, cutoff=2)
		
		# get all new middle nodes between u,v to rewire
		# if path len = 2 it is the u,v path 
		for path in paths:
			if len(path)>2:
				if path[1] in newNodes:
					nodes.add((path[1], distance(graph, u, path[1])))
		
		nodes = sorted(nodes,key=getKey)		
		finalEdge = [u] + [n[0] for n in nodes] + [v]

		for i in range(1,len(finalEdge)-2):
			source = finalEdge[i]
			target = finalEdge[i+1]

			originalAttributes = graph[u][target]
			customAttributes = originalAttributes.copy()
			
			if 'length' in originalAttributes:
				uSourceLength = graph[u][source]['length']
				uTargetLength = graph[u][target]['length']
				length = uTargetLength - uSourceLength
				customAttributes['length'] = length

			graph.add_edge(source, target, customAttributes)
			
			deleteUNodes.append(target)
			deleteVNodes.append(source)

		for node in deleteUNodes:
			graph.remove_edge(u, node)
		for node in deleteVNodes:
			graph.remove_edge(node, v)
		
		try:
			graph.remove_edge(u,v)
		except Exception, e:
			raise e

	return graph
		

if __name__ == "__main__":
	testGraph = nx.Graph()
	testGraph.add_node(1,longitude=1.0, latitude=1.0)
	testGraph.add_node(2,longitude=2.0, latitude=1.0)
	testGraph.add_node(3,longitude=3.0, latitude=3.0)
	testGraph.add_edge(1, 2,osmid=3,highway='residential',level=3, lanes=1, oneway=False)
	testGraph.add_edge(2, 3,osmid=4,highway='residential',level=3, lanes=1, oneway=False)
	newnodes = []
	newnodes.append((1.2, 1.8))
	newnodes.append((1.5, 1.8))
	newnodes.append((1.6, 1.8))
	newnodes.append((1.8, 1.8))
	newnodes.append((1.4, 1.8))
	newnodes.append((2.8, 2.2))
	newnodes.append((4, 4))

	print testGraph.nodes()

	import matplotlib.pyplot as plt
	
	G = linkNewNodes(testGraph, newnodes)
	print testGraph.nodes(data=True)

	print 'there a',len(testGraph.nodes()),'nodes'
	print testGraph[3]
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

	plt.show()



