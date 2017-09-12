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


import networkx as nx
import policosm.geoNetworks as pocogeo
from policosm.functions.getRtree import *
from shapely.geometry import MultiPoint
import shapely.wkt
import shapely
import csv 
import geojson

graph = nx.read_gexf('/Users/fabien/Downloads/shanghai_china.osm.gexf', node_type=None, relabel=False, version='1.1draft')
graph = pocogeo.clean(graph)
print 'graph was cleaned'

hospitals = []
hospitals_osmids = []

with open('/Users/fabien/Downloads/shanghai_hospital.csv') as fp:
	results = csv.reader(fp)
	next(results)
	for result in results:
		if result[7] > 121:
			hospitals.append((float(result[7]), float(result[8])))

print 'csv was read'
graph = pocogeo.linkNewNodes(graph, hospitals)

r = getGraphRtree(graph,generator='nodes',filename=None,interleaved=True)
for hospital in hospitals:
	x,y = hospital
	hits = r.nearest((x, y, x, y), 3, objects="raw")
	n =  pocogeo.nearestNodeFromLonLat(graph, x, y, list(hits))
	hospitals_osmids.append(n)

epsg = 4479
graph = pocogeo.addMetricDistanceToEdges(graph, epsg)
graph = pocogeo.simplify_with_rdp(graph)
graph = pocogeo.addTimeTraveltoEdges(graph, transportation=['motorist'])
# graph = pocogeo.convertNodesCoordinates(graph,4326,epsg)

cutoffs = [30, 60, 90, 180, 300, 600, 1200]
convexHulls = []
for cutoff in cutoffs:
	print cutoff, 'started'
	for osm_id in hospitals_osmids:
		lengths, path = nx.single_source_dijkstra(G=graph, source=osm_id, weight='motorist', cutoff=cutoff)
		leafs = lengths.keys()
		# print leafs
		hull = []
		for leaf in leafs:
			lat = graph.node[leaf]['latitude']
			lon = graph.node[leaf]['longitude']
			hull.append((lon, lat))
		# polygon = shapely.wkt.loads(MultiPoint(hull).convex_hull.wkt)

		g = geojson.Feature(geometry=MultiPoint(hull).convex_hull,id=osm_id, properties={'cutoff':cutoff})
		# print g 
		convexHulls.append(g)
	with open('/Users/fabien/Downloads/isochrone-'+str(cutoff)+'.geojson', 'w+') as fp:
		geojson.dump(geojson.FeatureCollection(convexHulls), fp, sort_keys=True)
		convexHulls=[]

