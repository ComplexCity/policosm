#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
clean roads graph created from osm file

parameters
graph

how it works
1 - remove nodes without geographic informations (latitude or longitude)
2 - remove self referencing edges (loop on itself)
3 - remove isolated nodes (degree is 0 )

return
graph minus alone or non-conform nodes

'''
import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

import matplotlib.pyplot as plt
from descartes.patch import PolygonPatch
import colorlover as cl
from shapely.geometry import Polygon, shape
import random

from policosm.extractors.roadsGraph import *
from policosm.extractors.buildingsPolygons import *
import policosm.geoNetworks as pocogeo
from policosm.functions import *

colors = [ (r/255,v/255,b/255) for r,v,b in cl.to_numeric(cl.scales['9']['seq']['Purples'])]
edgeWidth=[1,1,1,1,1,2,2,3,3]

def drawRoadsBuildingsMatplotlib(polygons,G,  displayRatio=1.0, edgeColorAttribute='level', edgeColorScale=9, nodeColorAttribute=None, nodeColorScale=None):
	fig = plt.figure()
	ax = fig.add_subplot(111)	

	pos={}
	for n in G.nodes():
		pos[n] = (G.node[n]['longitude'],G.node[n]['latitude'])

	# nodes
	nx.draw_networkx_nodes(G,pos,node_size=0,alpha=0.8,color=colors[-1], ax=ax)

	# edges
	for i in range(0,9):
		selectedEdges = [(u,v) for (u,v,d) in G.edges(data=True) if d['level'] == i]
		selectedColors = [colors[i] for e in selectedEdges]
		nx.draw_networkx_edges(G,pos,edgelist=selectedEdges,width=edgeWidth[i],edge_color=selectedColors, ax=ax)
	selectedEdges = [(u,v) for (u,v,d) in G.edges(data=True) if d['level'] == -1]
	nx.draw_networkx_edges(G,pos,edgelist=selectedEdges,width=0.8,edge_color='r', ax=ax)

	for feature in polygons['features']:
		if displayRatio < 1.0:
			if random.random() >= displayRatio:
				continue
		polygon = shape(feature['geometry'])
		patch = PolygonPatch(polygon, facecolor='#FD7400', edgecolor='#FD7400', alpha=0.5, zorder=1)
		ax.add_patch(patch)
	
	bounds = getBuildingsBoundaries(polygons)
	minx, miny, maxx, maxy = bounds
	ax.set_xlim(minx,maxx)
	ax.set_ylim(miny,maxy)

	plt.show()

if __name__ == "__main__":
	# filename = '/Volumes/Fabien/Research/cities-pictures/data/France/1-pbf/74173.pbf'
	filename = '/Users/fabien/Downloads/pau-agglomeration.osm'
	graph = roadsGraph(filename)
	graph = pocogeo.clean(graph)

	polygons = buildingsPolygons(filename)
	centroids = getCentroidsFromBuildingsPolygons(polygons)
	print len(centroids), centroids[0]
	graph = pocogeo.linkNewNodes(graph, centroids, level=-1)
	drawRoadsBuildingsMatplotlib(polygons,graph)