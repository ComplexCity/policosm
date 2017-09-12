#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in June 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
clean roads graph created from osm file

parameters
graph

how it works

return

'''
import matplotlib.pyplot as plt
import networkx as nx
import colorlover as cl
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import math

from policosm.extractors.roadsGraph import *
import policosm.geoNetworks as pocogeo
from policosm.functions import *
from policosm.functions.getRtree import *
from policosm.geoFunctions.getEPSG import *

colors = [ (r/255,v/255,b/255) for r,v,b in cl.to_numeric(cl.scales['9']['seq']['Purples'])]
colors2 = [ (r/255,v/255,b/255) for r,v,b in cl.to_numeric(cl.scales['9']['seq']['Oranges'])]
edgeWidth=[1,1,1,1,1,2,2,3,3]

fig = plt.figure()
ax = fig.add_subplot(111)	
polygons = []
slowestHumanSpeed=3000/1440 # "3km/h expressed in m/s"

def drawCircles(graph, tree, cutoff):
	for k,v in tree[0].iteritems():
		x,y = graph.node[k]['longitude'], graph.node[k]['latitude']
		circleRadius = slowestHumanSpeed * (cutoff-v)
		point = Point(x,y).buffer(circleRadius)
		polygons.append(point)
		# patch = PolygonPatch(point, facecolor=colors[-1], edgecolor=colors[-1], alpha=0.5, zorder=1)
		# ax.add_patch(patch)

def drawTrapezoid(graph, tree, cutoff):
	for k,v in tree[1].iteritems():
		if len(v) > 1:
			for i in range(0,len(v)-1):
				c1 = v[i]
				c2 = v[i+1]
				c1x, c1y = graph.node[c1]['longitude'], graph.node[c1]['latitude']
				c2x, c2y = graph.node[c2]['longitude'], graph.node[c2]['latitude']

				adjacent = abs(c1x-c2x)
				hypothenuse = math.sqrt((c2x-c1x)**2+(c2y-c1y)**2)
				angle = math.acos(adjacent/hypothenuse) #quadrant 1
				
				if c1x > c2x and c2y >= c1y: # quadrant 2
					angle = math.pi - angle
				elif c1x > c2x and c2y < c1y: # quadrant 3
					angle = math.pi + angle
				elif c2x > c1x and c2y < c1y: # quadrant 4
					angle = 2*math.pi-angle
				angle += math.pi/2 # find the right angle
				
				circleRadius = slowestHumanSpeed * (cutoff-tree[0][c1])
				c1x1 = c1x + (circleRadius) * math.cos(angle)
				c1y1 = c1y + (circleRadius) * math.sin(angle)
				c1x2 = c1x + (circleRadius) * math.cos(angle + math.pi)
				c1y2 = c1y + (circleRadius) * math.sin(angle + math.pi)
				circleRadius = slowestHumanSpeed * (cutoff-tree[0][c2])
				c2x1 = c2x + (circleRadius) * math.cos(angle)
				c2y1 = c2y + (circleRadius) * math.sin(angle)
				c2x2 = c2x + (circleRadius) * math.cos(angle + math.pi)
				c2y2 = c2y + (circleRadius) * math.sin(angle + math.pi)
				polygon = Polygon([(c1x1,c1y1),(c1x2,c1y2),(c2x2,c2y2),(c2x1,c2y1)])
				polygons.append(polygon)
				# patch = PolygonPatch(polygon, facecolor=colors[-1], edgecolor=colors[-1], alpha=0.5, zorder=1)
				# ax.add_patch(patch)

def drawRoads(G, edgeColorAttribute='level', edgeColorScale=9, nodeColorAttribute=None, nodeColorScale=None):
		
	pos={}
	for n in G.nodes():
		pos[n] = (G.node[n]['longitude'],G.node[n]['latitude'])

	# nodes
	nx.draw_networkx_nodes(G,pos,node_size=0,alpha=0.5,color=colors[-1])

	# edges
	for i in range(0,9):
		selectedEdges = [(u,v) for (u,v,d) in G.edges(data=True) if d['level'] == i]
		selectedColors = [colors[i] for e in selectedEdges]
		nx.draw_networkx_edges(G,pos,edgelist=selectedEdges,width=edgeWidth[i],edge_color=selectedColors, alpha=0.5)
	


if __name__ == "__main__":
	# filename = '/Users/fabien/workspace/github/policosm/tests/data/fake-city.osm'
	filename = '/Users/fabien/workspace/github/policosm/policosm/tests/01249.pbf'
	graph = roadsGraph(filename)
	graph = pocogeo.clean(graph)
	
	x, y = (4.9528934,45.8224652)
	graph = pocogeo.linkNewNodes(graph, [(x,y)])

	r = getGraphRtree(graph,generator='nodes',filename=None,interleaved=True)
	hits = r.nearest((x, y, x, y), 3, objects="raw")
	n =  pocogeo.nearestNodeFromLonLat(graph, x, y, list(hits))

	epsg = epsgFromCoordinates('France', x, y)
	graph = pocogeo.simplify_with_rdp(graph)
	graph = pocogeo.addMetricDistanceToEdges(graph, int(epsg))
	graph = pocogeo.addTimeTraveltoEdges(graph, transportation=['motorist'])
	graph = pocogeo.convertNodesCoordinates(graph,4326,3946)

	cutoffs = [30, 60, 90, 180, 300, 600]
	#cutoffs = [10000]

	for cutoff in cutoffs:
		polygons = []
		tree = nx.single_source_dijkstra(G=graph, source=n, weight='motorist', cutoff=cutoff)
		drawCircles(graph, tree, cutoff)
		drawTrapezoid(graph, tree, cutoff)
		union = cascaded_union(polygons)
		patch = PolygonPatch(union, facecolor=colors2[-1], edgecolor=colors2[-1], alpha=0.15, zorder=1)
		ax.add_patch(patch)
	drawRoads(graph)
	plt.show()