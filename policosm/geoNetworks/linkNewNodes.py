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

import sys
sys.path.insert(0, '/Users/fabien/Documents/workspace/github/policosm')

import json
import hashlib
import networkx as nx

from shapely.geometry import LineString, Point

from policosm.functions.getRtree import *

def nearestEdgeFromPoint(candidates, point):
	nearestCouple = {}
	for candidate in candidates:
		print ("Candidat : ", candidate)
		print ("Point : ", point)
		line = json.loads(candidate)
		nearestCouple[point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
	print(nearestCouple)
	mindistance = min(nearestCouple.keys())
	return nearestCouple[mindistance]

def distance(graph, source, target):
	point = Point((graph.node[source]['longitude'], graph.node[source]['latitude']))
	return point.distance(Point((graph.node[target]['longitude'], graph.node[target]['latitude'])))

def getKey(item):
    return item[1]

# def nearestNode(graph, source, candidates):
# 	point = Point((graph.node[source]['longitude'], graph.node[source]['latitude']))
# 	nearestNode = {}
# 	for candidate in candidates:
# 		nearestNode[point.distance(Point((graph.node[candidate]['longitude'], graph.node[candidate]['latitude'])))] = candidate
# 	mindistance = min(nearestNode.keys())
# 	return nearestNode[mindistance]

def nearestNodeFromLonLat(graph, longitude, latitude, candidates):
	source = Point(longitude, latitude)
	nearestNode = {}
	for candidate in candidates:
		point = json.loads(candidate)
		nearestNode[source.distance(Point(point['geometry']['coordinates']))] = point['id']
	mindistance = min(nearestNode.keys())
	return nearestNode[mindistance]


def linkNode_OSM(graph, node, edge,diriged = False, bus=False, epsgCode=4326, level=2, highway='path', threshold=0.0):

	modifiedEdges, newNodes = set(), set()

	z = Point(graph.nodes[node]['longitude'],graph.nodes[node]['latitude'])

	# get the closest edge from the new node to wire it to it 
	u,v =  edge[0], edge[1]

	# we got the nearest edge source and target
	# if the projection of the new node z is inside the segment ([–o——] and not o [–———])
	# 		we create a new node w on the edge and redistribute length
	ucoo = (graph.nodes[u]['longitude'], graph.nodes[u]['latitude'])
	vcoo = (graph.nodes[v]['longitude'], graph.nodes[v]['latitude'])
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
		#print "COUCOU"
		x,y = line.interpolate(segmentLength).coords[0]
		#print x,y, "COUCOU"
		w = Point(x,y)
		wid  = -int(hashlib.md5(w.wkt).hexdigest(), 16)
		newNodes.add(wid)

		#print graph.has_edge(u,v)
		#print graph.has_edge(v,u)

		if bus == False :
			graph.add_node(wid,longitude=x, latitude=y, utilisation='Linked(NoRtree)')
		else :
			graph.add_node(wid,longitude=x, latitude=y, utilisation='Linked(NoRtree)')
		
		if diriged :
			if graph.has_edge(u,v) :
				attributes = graph.get_edge_data(u,v)

				if type(graph) == nx.classes.multidigraph.MultiDiGraph : 
					for key,value in attributes.items() :

						uwAttributes = value.copy()
						wvAttributes = value.copy()

						#if 'length' in value:
							#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
							#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
						
						uwAttributes['policosm'] = True
						wvAttributes['policosm'] = True

						graph.remove_edge(u,v,key)
						
						ka = graph.add_edge(u,wid)
						kb = graph.add_edge(wid,v)
						Attributes = {(u,wid,ka) : uwAttributes, (wid,v,kb) : wvAttributes}

						nx.set_edge_attributes(graph,Attributes)

				else :
					attributes = graph[u][v]

					uwAttributes = attributes.copy()
					wvAttributes = attributes.copy()

					#if 'length' in attributes:
						#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
						#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
					
					uwAttributes['policosm'] = True
					wvAttributes['policosm'] = True

					graph.remove_edge(u,v)
					
					Attributes = {(u,wid) : uwAttributes, (wid,v) : wvAttributes}
					graph.add_edge(u,wid)
					graph.add_edge(wid,v)
					nx.set_edge_attributes(graph,Attributes)					


			if graph.has_edge(v,u) :
				attributes = graph.get_edge_data(v,u)

				if type(graph) == nx.classes.multidigraph.MultiDiGraph : 
					for key,value in attributes.items() :

						uwAttributes = value.copy()
						wvAttributes = value.copy()

						#if 'length' in value:
							#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
							#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
						
						uwAttributes['policosm'] = True
						wvAttributes['policosm'] = True

						graph.remove_edge(v,u,key)
						
						ka = graph.add_edge(v,wid)
						kb = graph.add_edge(wid,u)
						Attributes = {(v,wid,ka) : uwAttributes, (wid,u,kb) : wvAttributes}

						nx.set_edge_attributes(graph,Attributes)

				else :
					attributes = graph[v][u]

					uwAttributes = attributes.copy()
					wvAttributes = attributes.copy()

					#if 'length' in attributes:
						#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
						#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
					
					uwAttributes['policosm'] = True
					wvAttributes['policosm'] = True

					graph.remove_edge(v,u)
					
					Attributes = {(v,wid) : uwAttributes, (wid,u) : wvAttributes}
					graph.add_edge(v,wid)
					graph.add_edge(wid,u)
					nx.set_edge_attributes(graph,Attributes)

		else :
			attributes = graph[u][v]

			uwAttributes = attributes.copy()
			wvAttributes = attributes.copy()
			
			uwAttributes['policosm'] = True
			wvAttributes['policosm'] = True

			graph.remove_edge(u,v)
			
			Attributes = {(u,wid) : uwAttributes, (wid,v) : wvAttributes}
			graph.add_edge(u,wid)
			graph.add_edge(wid,v)
			nx.set_edge_attributes(graph,Attributes)					

	return (graph,wid,u,v)

def linkNode_OSM_Rtree(graph, node, dict_of_edge_id, diriged = False, details=False, rtreefile=None, csvfile = None, bus=False, epsgCode=4326, level=2, highway='path', threshold=0.0):
	
	modifiedEdges, newNodes = set(), set()

	z = Point( graph.nodes[node]['longitude'], graph.nodes[node]['latitude'])

	# get the closest edge from the new node to wire it to it 
	hits = list(rtreefile.nearest((z.x, z.y, z.x,z.y), 15, objects="raw"))
	
	if details :
		print ("LIST OF 15 NEAREST EDGES", hits)

	nearestCouple = {}
	for k in range (len(hits)):
		#print "Candidat : ", hits[k]
		#print "Point : ", z
		line = json.loads(hits[k])
		nearestCouple[z.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
	#print nearestCouple
	if (0 in nearestCouple) and (len(nearestCouple) > 1) :
		nearestCouple.pop(0)
	mindistance = min(nearestCouple.keys())

	if details :
		print("CHOOSEN EDGE",mindistance, nearestCouple[mindistance])
	
	u,v = nearestCouple[mindistance][0], nearestCouple[mindistance][1]

	while (not graph.has_edge(u,v)) and (not graph.has_edge(v,u)) :
		print("PROBLEM LINK RTREE WITH ", u, "AND", v, graph.has_edge(u,v),  graph.has_edge(v,u))
		if csvfile != None :
			txt = str(u) + ";" + str(v)
			csvfile.write(txt)
		nearestCouple.pop(mindistance)
		if len(nearestCouple) > 0 :
			mindistance = min(nearestCouple.keys())
			u,v = nearestCouple[mindistance][0], nearestCouple[mindistance][1]
		else :
			"... NO MATCHES"
			return 0
	#print u,graph.nodes[u],v,graph.nodes[u]
	# we got the nearest edge source and target
	# if the projection of the new node z is inside the segment ([–o——] and not o [–———])
	# 		we create a new node w on the edge and redistribute length
	ucoo = (graph.nodes[u]['longitude'], graph.nodes[u]['latitude'])
	vcoo = (graph.nodes[v]['longitude'], graph.nodes[v]['latitude'])
	line = LineString([ucoo,vcoo])
	lineLength = line.length
	segmentLength = line.project(z)

	if details :
		print("INFORMATIONS",segmentLength, lineLength, diriged, graph.has_edge(u,v), graph.has_edge(v,u) , u, v)

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

			
		if diriged :

			if graph.has_edge(u,v) :

				graph.add_node(wid,longitude=x, latitude=y, utilisation='Linked(WithRtree)', rTreeD = True)
				attributes = graph.get_edge_data(u,v)

				if type(graph) == nx.classes.multidigraph.MultiDiGraph : 
					for key,value in attributes.items() :

						uwAttributes = value.copy()
						wvAttributes = value.copy()

						#if 'length' in value:
							#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
							#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
						
						uwAttributes['policosm'] = True
						wvAttributes['policosm'] = True

						graph.remove_edge(u,v,key)
						
						ka = graph.add_edge(u,wid)
						kb = graph.add_edge(wid,v)
						Attributes = {(u,wid,ka) : uwAttributes, (wid,v,kb) : wvAttributes}

						nx.set_edge_attributes(graph,Attributes)

						try :
							rtreefile.delete( dict_of_edge_id[str(u) + '-' + str(v) + '-' + str(key)], (min(ucoo[0],vcoo[0]),min(ucoo[1],vcoo[1]),max(ucoo[0],vcoo[0]),max(ucoo[1],vcoo[1])) )
							dict_of_edge_id.pop(str(u) + '-' + str(v) + '-' + str(key))
						except Exception as e:
							print (e, "ERROR")

						x1 = graph.node[u]['longitude']
						x2 = graph.node[wid]['longitude']
						y1 = graph.node[u]['latitude']
						y2 = graph.node[wid]['latitude']

						minx = min([x1,x2])
						maxx = max([x1,x2])
						miny = min([y1,y2])
						maxy = max([y1,y2])
						linestring = geojson.LineString([(x1, y1), (x2, y2)])
						feature = geojson.Feature(geometry=linestring, properties={"node1": u ,"node2": wid}) 
						rtreefile.insert( int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy) , geojson.dumps(feature, sort_keys=True))
						dict_of_edge_id[str(u) + '-' + str(wid) + '-' + str(ka)] = int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

						x1 = graph.node[wid]['longitude']
						x2 = graph.node[v]['longitude']
						y1 = graph.node[wid]['latitude']
						y2 = graph.node[v]['latitude']

						minx = min([x1,x2])
						maxx = max([x1,x2])
						miny = min([y1,y2])
						maxy = max([y1,y2])
						linestring = geojson.LineString([(x1, y1), (x2, y2)])
						feature = geojson.Feature(geometry=linestring, properties={"node1": wid ,"node2": v}) 
						rtreefile.insert( int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )
						dict_of_edge_id[str(wid) + '-' + str(v) + '-' + str(kb)] = int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)			

					if details :
						print ("CASE 1", graph.has_edge(u,v), graph.has_edge(u,wid), graph.has_edge(wid,v))

				else :
					attributes = graph[u][v]

					uwAttributes = attributes.copy()
					wvAttributes = attributes.copy()

					#if 'length' in attributes:
						#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
						#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
					
					uwAttributes['policosm'] = True
					wvAttributes['policosm'] = True

					graph.remove_edge(u,v)
					
					Attributes = {(u,wid) : uwAttributes, (wid,v) : wvAttributes}
					graph.add_edge(u,wid)
					graph.add_edge(wid,v)
					nx.set_edge_attributes(graph,Attributes)					
					
					rtreefile.delete( dict_of_edge_id[str(u) + '-' + str(v)], (min(ucoo[0],vcoo[0]),min(ucoo[1],vcoo[1]),max(ucoo[0],vcoo[0]),max(ucoo[1],vcoo[1])) )
					dict_of_edge_id.pop(str(u) + '-' + str(v))

					x1 = graph.node[u]['longitude']
					x2 = graph.node[wid]['longitude']
					y1 = graph.node[u]['latitude']
					y2 = graph.node[wid]['latitude']

					minx = min([x1,x2])
					maxx = max([x1,x2])
					miny = min([y1,y2])
					maxy = max([y1,y2])
					linestring = geojson.LineString([(x1, y1), (x2, y2)])
					feature = geojson.Feature(geometry=linestring, properties={"node1": u ,"node2": wid}) 
					rtreefile.insert( int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )
					dict_of_edge_id[str(u) + '-' + str(wid)] = int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

					x1 = graph.node[v]['longitude']
					x2 = graph.node[wid]['longitude']
					y1 = graph.node[v]['latitude']
					y2 = graph.node[wid]['latitude']

					minx = min([x1,x2])
					maxx = max([x1,x2])
					miny = min([y1,y2])
					maxy = max([y1,y2])
					linestring = geojson.LineString([(x1, y1), (x2, y2)])
					feature = geojson.Feature(geometry=linestring, properties={"node1": wid ,"node2": v}) 
					rtreefile.insert( int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )	
					dict_of_edge_id[str(wid) + '-' + str(v)] = int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

					if details :
						print ("CASE 2", graph.has_edge(u,v), graph.has_edge(u,wid), graph.has_edge(wid,v))

			if graph.has_edge(v,u) :

				graph.add_node(wid,longitude=x, latitude=y, utilisation='Linked(WithRtree)', rTreeD = True)
				attributes = graph.get_edge_data(v,u)

				if type(graph) == nx.classes.multidigraph.MultiDiGraph : 
					for key,value in attributes.items() :

						uwAttributes = value.copy()
						wvAttributes = value.copy()

						#if 'length' in value:
							#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
							#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
						
						uwAttributes['policosm'] = True
						wvAttributes['policosm'] = True

						graph.remove_edge(v,u,key)

						ka = graph.add_edge(v,wid)
						kb = graph.add_edge(wid,u)
						Attributes = {(v,wid,ka) : uwAttributes, (wid,u,kb) : wvAttributes}

						nx.set_edge_attributes(graph,Attributes)

						try : 
							rtreefile.delete( dict_of_edge_id[str(v) + '-' + str(u) + '-' + str(key)], (min(ucoo[0],vcoo[0]),min(ucoo[1],vcoo[1]),max(ucoo[0],vcoo[0]),max(ucoo[1],vcoo[1])) )
							dict_of_edge_id.pop(str(v) + '-' + str(u) + '-' + str(key))
						except Exception as e:
							print (e, "ERROR")

						x1 = graph.node[u]['longitude']
						x2 = graph.node[wid]['longitude']
						y1 = graph.node[u]['latitude']
						y2 = graph.node[wid]['latitude']

						minx = min([x1,x2])
						maxx = max([x1,x2])
						miny = min([y1,y2])
						maxy = max([y1,y2])
						linestring = geojson.LineString([(x1, y1), (x2, y2)])
						feature = geojson.Feature(geometry=linestring, properties={"node1": u ,"node2": wid}) 
						rtreefile.insert( int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )
						dict_of_edge_id[str(v) + '-' + str(wid) + '-' + str(ka)] = int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

						x1 = graph.node[v]['longitude']
						x2 = graph.node[wid]['longitude']
						y1 = graph.node[v]['latitude']
						y2 = graph.node[wid]['latitude']

						minx = min([x1,x2])
						maxx = max([x1,x2])
						miny = min([y1,y2])
						maxy = max([y1,y2])
						linestring = geojson.LineString([(x1, y1), (x2, y2)])
						feature = geojson.Feature(geometry=linestring, properties={"node1": wid ,"node2": v}) 
						rtreefile.insert( int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )
						dict_of_edge_id[str(wid) + '-' + str(u) + '-' + str(kb)] = int(hashlib.md5( str(value) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

					if details :
						print ("CASE 3", graph.has_edge(v,u), graph.has_edge(v,wid), graph.has_edge(wid,u))

				else :
					attributes = graph[v][u]

					uwAttributes = attributes.copy()
					wvAttributes = attributes.copy()

					#if 'length' in attributes:
						#uwAttributes['length'] = addMetricDistanceToEdge(ucoo[0], ucoo[1], w.x, w.y, epsgCode)
						#wvAttributes['length'] = addMetricDistanceToEdge(vcoo[0], vcoo[1], w.x, w.y, epsgCode)
					
					uwAttributes['policosm'] = True
					wvAttributes['policosm'] = True

					graph.remove_edge(v,u)
					
					Attributes = {(v,wid) : uwAttributes, (wid,u) : wvAttributes}
					graph.add_edge(v,wid)
					graph.add_edge(wid,u)
					nx.set_edge_attributes(graph,Attributes)

					rtreefile.delete( dict_of_edge_id[str(v) + '-' + str(u)], (min(ucoo[0],vcoo[0]),min(ucoo[1],vcoo[1]),max(ucoo[0],vcoo[0]),max(ucoo[1],vcoo[1])) )
					dict_of_edge_id.pop(str(v) + '-' + str(u))
					
					x1 = graph.node[u]['longitude']
					x2 = graph.node[wid]['longitude']
					y1 = graph.node[u]['latitude']
					y2 = graph.node[wid]['latitude']

					minx = min([x1,x2])
					maxx = max([x1,x2])
					miny = min([y1,y2])
					maxy = max([y1,y2])
					linestring = geojson.LineString([(x1, y1), (x2, y2)])
					feature = geojson.Feature(geometry=linestring, properties={"node1": u ,"node2": wid}) 
					rtreefile.insert( int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )
					dict_of_edge_id[str(v) + '-' + str(wid)] = int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

					x1 = graph.node[v]['longitude']
					x2 = graph.node[wid]['longitude']
					y1 = graph.node[v]['latitude']
					y2 = graph.node[wid]['latitude']

					minx = min([x1,x2])
					maxx = max([x1,x2])
					miny = min([y1,y2])
					maxy = max([y1,y2])
					linestring = geojson.LineString([(x1, y1), (x2, y2)])
					feature = geojson.Feature(geometry=linestring, properties={"node1": wid ,"node2": v}) 
					rtreefile.insert( int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16), (minx,miny,maxx,maxy), geojson.dumps(feature, sort_keys=True) )
					dict_of_edge_id[str(wid) + '-' + str(u)] = int(hashlib.md5( str(attributes) + str(x1) + str(x2) + str(y1) + str(y2) ).hexdigest(), 16)

					if details :
						print ("CASE 4", graph.has_edge(v,u), graph.has_edge(v,wid), graph.has_edge(wid,u))

	return (graph,wid,u,v,dict_of_edge_id,rtreefile)




