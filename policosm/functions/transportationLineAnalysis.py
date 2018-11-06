#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
In progress since June 2018 in ComplexCity Lab

@author: github.com/fpfaende

Object :
	Important functions for transportation analysis

Functions in this file :

	- time_travelling : calculate time travel from 2 (x,y) corrdinates and speed information 
	- elements_du_graphe : make a first analysis of the relation by drawing nodes and edges
	- analyse lexicale : try to find by name analysis the direction of the transportation line
	[...]
	- road_support : same as the road extractor, with some changes

'''

import os
import re
import sys
import json
import math
import json
import geojson
import hashlib
import networkx as nx
import matplotlib.pyplot as plt

from shapely.geometry import Polygon, LineString, Point, shape

sys.path.insert(0, '/home/alex/Bureau/policosm')
from utils.roads import levels
from geoNetworks.linkNewNodes import linkNode_OSM, linkNode_OSM_Rtree
from policosm.geoNetworks.addMetricDistanceToEdges import addMetricDistanceToEdge

# Default values
	#Default waiting time
waiting_bus_time = 15.0/60.0 # hour unit
waiting_trm_time = 10.0/60.0 # hour unit
waiting_sub_time = 04.0/60.0 # hour unit

	#Default speeds
average_ped_speed = 03.5 # km/h
average_bus_speed = 20.0 # km/h
average_trm_speed = 25.0 # km/h
average_sub_speed = 30.0 # km/h

def time_travelling (x1,x2,y1,y2,type_mobility):
	type_mobility = type_mobility.lower()
	x1,x2,y1,y2 = (x1*math.pi)/180, (x2*math.pi)/180, (y1*math.pi)/180, (y2*math.pi)/180
	try :
		distance = 6371.01* math.acos(math.cos(y1)*math.cos(y2)*math.cos(x2-x1) + math.sin(y1)*math.sin(y2))
	except Exception, e :
		print e, "Use default pythagorian theorem"
		x = (x1 - x2)
		y = (y1 - y2)
		distance = 78.85 * math.sqrt(x*x + y*y)

	if type_mobility == 'bus' or type_mobility == 'trolleybus':
		speed = average_bus_speed
	elif type_mobility == 'subway' :
		speed = average_sub_speed
	elif type_mobility == 'tram' or type_mobility=='light_rail' :
		speed = average_trm_speed
	elif type_mobility == 'pedestrian' :
		speed = average_ped_speed
	else :
		speed = average_ped_speed
		print 'Default pedestrian speed taken'
	time = float(distance) / float(speed)
	return time


def retropropogation(graph,diGraph,to_visit,visited,info_name,mobility,forward = True, details = False) :
	next_visits = []

	for node in to_visit :
		neighbors = list(graph[node])

		for neighbor in neighbors :
			if neighbor in visited :
				continue
			else :
				time = time_travelling(graph.nodes[node]['longitude'],graph.nodes[neighbor]['longitude'],graph.nodes[node]['latitude'],graph.nodes[neighbor]['latitude'],mobility)
				if details :
					print node, neighbor, diGraph.has_edge(node,neighbor), diGraph.has_edge(neighbor,node)
				if forward :
					if not diGraph.has_edge(node,neighbor) :
						diGraph.add_edge( node,neighbor, ligne = info_name, type_mobility=mobility, time_travel=time)
						visited.append(neighbor)
						next_visits.append(neighbor)
					else :
						continue
				else :
					if not diGraph.has_edge(neighbor,node) :
						diGraph.add_edge( neighbor,node, ligne = info_name, type_mobility=mobility, time_travel=time)
						visited.append(neighbor)
						next_visits.append(neighbor)
					else :
						continue

	return diGraph, next_visits, visited


def elements_du_graphe(fineGraph,isDiGraph,noDiGraph,keyOsmid,tags,members,nodes,ways,coords,default_counter,fichierCSV, csvData, stations_to_actualize , nodes_residue,type_tr = None):

	ways_in_relation, relation_station, relation_platforms = {},{},{}
	count_node_itown, count_node_ntown = 0, 0
	pos = {}
	
	# Analyse des éléments contenus dans la relation
	def analyse_relation (osmType,osmid,nodes,fineGraph,noDiGraph,isDiGraph,type_tr,count_node_itown,count_node_ntown,ways,relation_platforms,ways_in_relation,info_name, stations_to_actualize , nodes_residue):
		# Stations de la relation
		try :
			if osmType == 'node':
				if osmid in nodes:
					# Si la station est dans les données exportées alors on l'intègre dans le graphe
					#	GENERAL INFORMATIONS
					node_info = nodes[osmid]
					osmid, lon, lat = int(osmid), float(node_info['coords'][0]), float(node_info['coords'][1])
					st_name = node_info['name'] if ('name' in node_info) else 'NO_NAME'
					utiliZation = "Bus Station" if type_tr == 'bus' else "Subway Station" if type_tr == 'subway' else "Tramway Station" if type_tr == 'tram' else "Light Rail Station" if type_tr == 'light_rail' else "Undfined Station"

					#	GENERAL CRITERIAS
					is_publict_stop_pos = True if 'public_transport' in node_info and node_info['public_transport']=='stop_position' else False
					is_publict_stop_plt = True if 'public_transport' in node_info and node_info['public_transport']=='platform' else False #platform is allowed here due to node type of osmType

					#	BUS STATION CRITERIAS
					is_highway_bus_stop = True if 'highway' in node_info and node_info['highway']=='bus_stop' else False
					is_bus 				= True if 'bus' in node_info and node_info['bus']=='yes' else False
					is_trolley			= True if 'trolleybus' in node_info and node_info['trolleybus'] == 'yes' else False
					is_busamenity		= True if 'amenity' in node_info and node_info['amenity'] == 'bus_station' else False

					is_bus_station 		=  is_highway_bus_stop or ( (is_publict_stop_pos or is_publict_stop_plt) and (is_bus) ) or is_busamenity
					is_trlybus_station 	=  is_highway_bus_stop or ( (is_publict_stop_pos or is_publict_stop_plt) and (is_trolley) ) or is_busamenity

					#	SUBWAY STATION CRITERIAS
					is_station_subway	= True if 'station' in node_info and node_info['station'] == 'subway' else False
					is_subway 			= True if 'subway' in node_info and node_info['subway'] == 'yes' else False

					is_subway_station 	= is_subway or is_station_subway

					#	TRAM STATION CRITERIAS
					is_tram				= True if 'tram' in node_info and node_info['tram']=='yes' else False
					is_tramstop			= True if 'railway' in node_info and node_info['railway']=='tram_stop' else False

					is_tram_station 	= ((is_publict_stop_pos or is_publict_stop_plt) and (is_tram)) or is_tramstop

					#	LIGHT RAIL STATION CRITERIAS
					is_light_rail		= True if 'light_rail' in node_info and node_info['light_rail']=='yes' else False

					is_light_station 	= (is_publict_stop_pos or is_publict_stop_plt) and (is_light_rail)


					if is_bus_station or is_subway_station or is_tram_station or is_light_station or is_trlybus_station :
						fineGraph.add_node(osmid,longitude=lon, latitude=lat, utilisation=utiliZation, nom=st_name, ligne=info_name)
						noDiGraph.add_node(osmid,longitude=lon, latitude=lat, utilisation=utiliZation, nom=st_name, ligne=info_name)
						isDiGraph.add_node(osmid,longitude=lon, latitude=lat, utilisation=utiliZation, nom=st_name, ligne=info_name)
						node_info['name'] = "DEFAULT NAME" if not 'name' in node_info else node_info['name']
						relation_station[osmid] = node_info
						count_node_itown += 1
						pos[osmid] = (float(node_info['coords'][0]),float(node_info['coords'][1]))
						stations_to_actualize[osmid] = {'utilisation':utiliZation, 'nom':st_name, 'ligne':info_name}

						if csvData :
							fichierCSV.write(str(float(node_info['coords'][0])) + ";" + str(float(node_info['coords'][1])) + "\n")
					else : 
						print "Finalement pas de noeud ?", node_info
						nodes_residue += 1

					return (fineGraph,noDiGraph,isDiGraph,count_node_itown,count_node_ntown,relation_station,relation_platforms,ways_in_relation, stations_to_actualize , nodes_residue)

				else:
					return (fineGraph,noDiGraph,isDiGraph,count_node_itown,count_node_ntown,relation_station,relation_platforms,ways_in_relation, stations_to_actualize , nodes_residue)
					count_node_ntown += 1
		
			# Chemins de la relation == tuple : (list of nodes, dict of tags)
			elif osmType == 'way':
				if osmid in ways : 
					way_nodes = ways[osmid]['nds']
					way_tag = ways[osmid]['tags']

					# WAYS CRITERIAS
					is_way_platform = True if 'highway' in way_tag and way_tag['highway'] == 'platform' else False
					is_way_bus_stop = True if 'highway' in way_tag and way_tag['highway'] == 'bus_stop' else False
					is_way_pub_pltf = True if 'public_transport' in way_tag and way_tag['public_transport'] == 'platform' else False

					if (is_way_platform) or (is_way_bus_stop) or (is_way_pub_pltf):
						relation_platforms[osmid] = (way_nodes,way_tag,info_name)
					else : 							
						if not osmid in ways_in_relation :
							ways_in_relation[osmid] = (way_nodes,way_tag,info_name)

						else :
							lowest = 0
							while str(osmid)+str(lowest) in ways_in_relation :
								lowest += 1
							ways_in_relation[str(osmid)+str(lowest)] = (way_nodes,way_tag,info_name)

				else :
					print "NO WAY FOUND FOR", osmid

				return (fineGraph,noDiGraph,isDiGraph,count_node_itown,count_node_ntown,relation_station,relation_platforms,ways_in_relation, stations_to_actualize , nodes_residue)

			else :
				print "NOT TREATED TYPE", osmType
				return (fineGraph,noDiGraph,isDiGraph,count_node_itown,count_node_ntown,relation_station,relation_platforms,ways_in_relation, stations_to_actualize , nodes_residue)
				
		except Exception, e:
			print "ERROR BETWEEN LINE 110 and 200", e
			return (fineGraph,noDiGraph,isDiGraph,count_node_itown,count_node_ntown,relation_station,relation_platforms,ways_in_relation, stations_to_actualize , nodes_residue)

	# Information sur la ligne
	# Lister les éléments contenus dans la zone d'export et dans la relation

	# SI on doit traiter une ligne de transport ou une relation de station de métro
	if type_tr != 'stop_area' :

		info_name = tags['name'] if 'name' in tags else "DEFAULT LINE " + str(default_counter) + " : FOR "+ str(type_tr.upper())
		default_counter = default_counter if 'name' in tags else default_counter+1

		print "NEW LINE INITIALIZATION FOR : ", info_name, " -- TRANSPORTATION TYPE : " , type_tr

		for elem in range (len(members)):
			osmid, osmType,osmDetail = members[elem]['ref'], members[elem]['type'], members[elem]['role']
			R = analyse_relation (osmType,osmid,nodes,fineGraph,noDiGraph,isDiGraph,type_tr,count_node_itown,count_node_ntown,ways,relation_platforms,ways_in_relation,info_name, stations_to_actualize , nodes_residue)
			fineGraph,noDiGraph,isDiGraph,count_node_itown,count_node_ntown,relation_station,relation_platforms,ways_in_relation, stations_to_actualize , nodes_residue = R[0], R[1], R[2], R[3], R[4], R[5], R[6], R[7], R[8], R[9]
		
		# Tracer le graphe intermédiaire
			# On transfère les liens dans le graphe intermédiaire avant traitement
		nds = list(noDiGraph.nodes)
		for key,value in ways_in_relation.items() :
			list_of_nodes = value[0]
			constructible = []
			try :
				for nodei in range (len(list_of_nodes)) :
					the_node = int(list_of_nodes[nodei])
					lon, lat = nodes[the_node]['coords'][0], nodes[the_node]['coords'][1]
					if not(nodei in relation_station) or not(nodei in nds) :
						isDiGraph.add_node(the_node,longitude=lon, latitude=lat, utilisation="Circulation", ligne=info_name)
						noDiGraph.add_node(the_node,longitude=lon, latitude=lat, utilisation="Circulation", ligne=info_name)
						fineGraph.add_node(the_node,longitude=lon, latitude=lat, utilisation="Circulation", ligne=info_name)
					
					pos[the_node] = (lon,lat)
					constructible.append(the_node)
			except KeyError :
				print the_node, " NOT IN FILE"
				pass

			for nodei in range (1,len(constructible)) :
				time = time_travelling(nodes[int(constructible[nodei-1])]['coords'][0], nodes[int(constructible[nodei])]['coords'][0], nodes[int(constructible[nodei-1])]['coords'][1], nodes[int(constructible[nodei])]['coords'][1], type_tr)
				noDiGraph.add_edge( int(constructible[nodei-1]), int(constructible[nodei]), ligne=value[-1], time_travel = time)

			ways_in_relation[key] = (constructible,value[1])

		if type_tr == 'rien' :
			nx.draw_networkx_nodes(noDiGraph,pos,node_size=5)
			nx.draw_networkx_edges(noDiGraph,pos,edgelist=list(noDiGraph.edges),width=3)
			plt.show()
			nx.write_gexf(noDiGraph,'inspection.gexf')
		
		print "TOTAL NODES : " + str(count_node_itown+count_node_ntown) + "\tNODES IN FILE : " + str(count_node_itown) + "\tNOEUDS OUT : " + str(count_node_ntown)
		
		#nx.draw_networkx_nodes(noDiGraph,pos,node_size=5)
		#nx.draw_networkx_edges(noDiGraph,pos,edgelist=list(noDiGraph.edges),width=3)
		#plt.show()
		return (fineGraph, isDiGraph, noDiGraph, ways_in_relation, relation_station, relation_platforms, info_name, default_counter, stations_to_actualize , nodes_residue)

	else :
		print "STOP AREA DETECTED : RELATION ANALYSIS"
		subway_platforms, stop_node, entrances = {}, {}, {}
		longs, latts, out_nodes = [], [], []

		for elem in range (len(members)):
			osmid, osmType,osmDetail = members[elem]['ref'], members[elem]['type'], members[elem]['role']
			if osmType == 'node' :
				try :
					node_info = nodes[osmid]
					if ('railway' in node_info) and (node_info['railway'] == 'subway_entrance'):
						entrances[osmid] = node_info
						fineGraph.add_node( osmid,longitude=node_info['coords'][0], latitude=node_info['coords'][1] ,utilisation="Subway Entrance")

					elif ( (('station' in node_info) and (node_info['station'] == 'subway')) or (('subway' in node_info) and (node_info['subway'] == 'yes'))) and ((('public_transport' in node_info) and (node_info['public_transport'] == 'stop_position')) or (('railway' in node_info) and (node_info['railway'] == 'stop')) or (('railway' in node_info) and (node_info['railway'] == 'station'))):
						stop_node[osmid] = node_info
						fineGraph.add_node( osmid,longitude=node_info['coords'][0], latitude=node_info['coords'][1] ,utilisation="Subway Station")				

					else :
						continue
				except KeyError :
					out_nodes.append(osmid)
					continue
			
		for key,value in stop_node.items() :
			longs.append(value['coords'][0])
			latts.append(value['coords'][1])

		if entrances != {} :
			if len(longs) > 1 :
				moy_longs = float(sum(longs)/len(longs))
				moy_latts = float(sum(latts)/len(longs))
				station_centroid = Point(moy_longs,moy_latts)
				adde  = -int(hashlib.md5(station_centroid.wkt).hexdigest(), 16)
				fineGraph.add_node(adde,longitude=moy_longs, latitude=moy_latts ,utilisation="Subway Station")

				for key,value in stop_node.items() :
					fineGraph.add_edge( adde, key, type_mobility='Pedestrian', time_travel=waiting_sub_time)
					fineGraph.add_edge( key, adde, type_mobility='Pedestrian', time_travel=0.0)

				for key,value in entrances.items() :
					time = time_travelling(moy_longs, nodes[key]['coords'][0], moy_latts, nodes[key]['coords'][1], 'pedestrian')
					fineGraph.add_edge( adde, key, type_mobility='Pedestrian', time_travel=time)
					fineGraph.add_edge( key, adde, type_mobility='Pedestrian', time_travel=time)

				if 'name' in tags :
					subway_platforms[tags['name']] = {'Stop_nodes' : stop_node, 'Entrances' : entrances , 'Centroid' : adde}
				else :
					subway_platforms[keyOsmid] = {'Stop_nodes' : stop_node, 'Entrances' : entrances , 'Centroid' : adde}

			elif len(longs) == 1 :
				for key,value in entrances.items() :
					time = time_travelling(nodes[stop_node.keys()[0]]['coords'][0], nodes[key]['coords'][0], nodes[stop_node.keys()[0]]['coords'][1], nodes[key]['coords'][1], 'pedestrian')
					fineGraph.add_edge( stop_node.keys()[0], key, type_mobility='Pedestrian', time_travel=time)
					fineGraph.add_edge( key, stop_node.keys()[0], type_mobility='Pedestrian', time_travel=time)

				if 'name' in tags :
					subway_platforms[tags['name']] = {'Stop_nodes' : stop_node, 'Entrances' : entrances , 'Centroid' : stop_node.keys()[0]}
				else :
					subway_platforms[keyOsmid] = {'Stop_nodes' : stop_node, 'Entrances' : entrances , 'Centroid' : stop_node.keys()[0]}				

			else :
				pass

		else :
			if len(longs)>0 :
				# If there is no entrance, creating a virtual subway entrance
				nds = list(fineGraph.nodes)
				moy_longs = float(sum(longs)/len(longs)) + 0.0001
				moy_latts = float(sum(latts)/len(longs))
				txt = str(moy_longs).encode('utf-8') + str(moy_latts).encode('utf-8')
				txt2 = txt.encode('ascii','ignore')
				adde  = int(hashlib.md5(txt2).hexdigest(), 16)
				while adde in nds :
					print adde, "ALREADY USED, ADDING 1"
					adde += 1
				fineGraph.add_node(adde,longitude=moy_longs, latitude=moy_latts ,utilisation="Created Subway Entrance")			
				time = time_travelling(nodes[stop_node.keys()[0]]['coords'][0], moy_longs, nodes[stop_node.keys()[0]]['coords'][1], moy_latts, 'pedestrian')
				fineGraph.add_edge( stop_node.keys()[0], adde, type_mobility='Pedestrian', time_travel=time)
				fineGraph.add_edge( adde, stop_node.keys()[0], type_mobility='Pedestrian', time_travel=time)

		print len(out_nodes), "NODES OU OF EXPORT ZONE STATION NETWORK"
		print "Subway network created with ", len(longs), " stations and " , len(entrances), " entrances "
		return [fineGraph]

	nx.draw_networkx_nodes(noDiGraph,pos,node_size=5)
	nx.draw_networkx_edges(noDiGraph,pos,edgelist=list(noDiGraph.edges),width=3)
	plt.show()

def analyse_lexicale (fineG,noDiG,isDiG,info,stations,fichier, tags, type_mobility = 'Unknown'):
	# noDig : Graphe non dirigé servant de support
	# isDiG : Graphe dirigé servant de support
	# info : nom de la ligne
	# stations : dict de dict de stations {osmid : {osmtag1 : osmvalue1 ...}}
	type_mobility = type_mobility.capitalize()
	#print type(info)
	if "DEFAULT" not in info :

		# STEP 1  : DETERMINE DEPARTURE AND ARRIVAL ID
		id_dep_iso = None
		id_arr_iso = None
		id_dep = None
		id_arr = None

		# 	METHOD A : SEARCH INTO TAGS
		depart = tags['from'] if 'from' in tags else None
		arrive   = tags['to']   if 'to'   in tags else None

		for key,value in stations.items() :

			id_dep_iso = key if (('name' in value) and (value['name'] != None) and (depart != None) and (value['name'] in depart) and (id_dep_iso == None)) else None
			id_dep = key if (('name' in value) and (value['name'] != None) and (depart != None) and (value['name'] in depart) and (id_dep == None) and (nx.degree(noDiG, int(key)) != 0)) else None

			id_arr_iso = key if (('name' in value) and (value['name'] != None) and (arrive != None) and (value['name'] in arrive) and (id_arr_iso == None)) else None
			id_arr = key if (('name' in value) and (value['name'] != None) and (arrive != None) and (value['name'] in arrive) and (id_arr == None) and (nx.degree(noDiG, int(key)) != 0)) else None

		#	METHOD B : SEARCH INTO LINE NAME
		if id_dep_iso == None and id_arr_iso == None :

			# BY DETERMINING DEPARTURE AND ARRIVAL FROM LINE NAME, PRIORITY IS ACCORDING TO LIST.INDEX PROCESS (MINIMUM INDEX OF MAXIMUM SEARCH)
			p = [ len(info.split(u'\u2192')), len(info.split(u'\u21d2')), len (info.split('->') ), len(info.split('=>')), len(info.split('>'))]
			q = [ info.split(u'\u2192'), info.split(u'\u21d2'), info.split('->'), info.split('=>'), info.split('>')]
			#print p,q
			if ( max(p) ==1) :
				print "Nous ne pouvons déterminer lexicalement les terminus pour ",  info
				return (fineG,noDiG,isDiG,0,depart,arrive)
			else :
				# WE CANNOT TREAT LINES LIKE 'A->B->C'
				terminus = q[p.index(max(p))]

				depart = terminus[0] if depart == None else depart
				arrive = terminus[1] if arrive == None else arrive

				for key,value in stations.items() :
					id_dep_iso = key if (('name' in value) and (value['name'] != None) and (value['name'] in depart) and (id_dep_iso == None)) else None
					id_dep = key if (('name' in value) and (value['name'] != None) and (value['name'] in depart) and (id_dep == None) and (nx.degree(noDiG, int(key)) != 0)) else None

					id_arr_iso = key if (('name' in value) and (value['name'] != None) and (value['name'] in arrive) and (id_arr_iso == None)) else None
					id_arr = key if (('name' in value) and (value['name'] != None) and (value['name'] in depart) and (id_arr == None) and (nx.degree(noDiG, int(key)) != 0)) else None

		print depart, id_dep, id_dep_iso, arrive, id_arr, id_arr_iso

		# CASE 1 : Final departure and arrival found
		if (id_dep != None) and (id_arr != None) :
			# Un relation déterminée lexicalement peut avoir ses stations terminaux non raccordées à la voie
			if (noDiG.degree[id_dep] == 0) :
				s_point = Point(noDiG.nodes[id_dep]['longitude'],noDiG.nodes[id_dep]['latitude'])
				nearestCouple = {}
				edges = list(noDiG.edges)
				for p in range (len(edges)):
					linestring = geojson.LineString([(noDiG.nodes[edges[p][0]]['longitude'],noDiG.nodes[edges[p][0]]['latitude']) , (noDiG.nodes[edges[p][1]]['longitude'],noDiG.nodes[edges[p][1]]['latitude'])])
					feature = geojson.Feature(geometry=linestring, properties={"node1": edges[p][0] ,"node2": edges[p][1]}) 
					candidate = geojson.dumps(feature)
					line = json.loads(candidate)
					nearestCouple[s_point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
				if nearestCouple != {} :
					proche_Edge = min(nearestCouple.keys())
					#print proche_Edge
					#print "A", nearestCouple[proche_Edge]
					if proche_Edge < 0.0001 :
						R = linkNode_OSM(noDiG,id_dep,nearestCouple[proche_Edge],diriged = True, bus = True)
						noDiG, new_node, u,v = R[0], R[1], R[2], R[3]
						if type_mobility == 'bus' :
							fineG.add_node(new_node, utilisation='Link Platform_BusLine', ligne = info)
							new_node_attributes = {new_node : noDiG.nodes[new_node]}
							nx.set_node_attributes(fineG,new_node_attributes)
							noDiG.add_edge(id_dep,new_node, type_mobility='Platform_to_Bus', ligne= info, time_travel=waiting_bus_time) # Entry
							noDiG.add_edge(new_node,id_dep, type_mobility='Platform_to_Bus', ligne= info, time_travel=0.0)
						else :
							fineG.add_node(new_node, utilisation='Link Platform_XxxLine', ligne = info)
							new_node_attributes = {new_node : noDiG.nodes[new_node]}
							nx.set_node_attributes(fineG,new_node_attributes)
							noDiG.add_edge(id_dep,new_node, type_mobility='Platform_to_Xxx', ligne= info, time_travel=5.0)
							noDiG.add_edge(new_node,id_dep, type_mobility='Platform_to_Xxx', ligne= info, time_travel=0.0)								
				
			if (noDiG.degree[id_arr] == 0) :
				s_point = Point(noDiG.nodes[id_arr]['longitude'],noDiG.nodes[id_arr]['latitude'])
				nearestCouple = {}
				edges = list(noDiG.edges)
				for p in range (len(edges)):
					linestring = geojson.LineString([(noDiG.nodes[edges[p][0]]['longitude'],noDiG.nodes[edges[p][0]]['latitude']) , (noDiG.nodes[edges[p][1]]['longitude'],noDiG.nodes[edges[p][1]]['latitude'])])
					feature = geojson.Feature(geometry=linestring, properties={"node1": edges[p][0] ,"node2": edges[p][1]}) 
					candidate = geojson.dumps(feature)
					line = json.loads(candidate)
					nearestCouple[s_point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
				if nearestCouple != {} :
					proche_Edge = min(nearestCouple.keys())
					#print proche_Edge
					#print "A", nearestCouple[proche_Edge]
					if proche_Edge < 0.0001 :
						R = linkNode_OSM(noDiG,id_arr,nearestCouple[proche_Edge],diriged = True, bus = True)
						noDiG, new_node, u,v = R[0], R[1], R[2], R[3]
						if type_mobility == 'bus' :
							fineG.add_node(new_node, utilisation='Link Platform_BusLine', ligne = info)
							new_node_attributes = {new_node : noDiG.nodes[new_node]}
							nx.set_node_attributes(fineG,new_node_attributes)
							noDiG.add_edge(id_dep,new_node, type_mobility='Platform_to_Bus', ligne= info, time_travel=waiting_bus_time)
							noDiG.add_edge(new_node,id_dep, type_mobility='Platform_to_Bus', ligne= info, time_travel=0.0)
						else :
							fineG.add_node(new_node, utilisation='Link Platform_XxxLine', ligne = info)
							new_node_attributes = {new_node : noDiG.nodes[new_node]}
							nx.set_node_attributes(fineG,new_node_attributes)
							noDiG.add_edge(id_dep,new_node, type_mobility='Platform_to_Xxx', ligne= info, time_travel=5.0)
							noDiG.add_edge(new_node,id_dep, type_mobility='Platform_to_Xxx', ligne= info, time_travel=0.0)	

			to_visita, visiteda, to_visitb, visitedb = [id_dep], [id_dep], [id_arr], [id_arr]
			compteura, compteurb = 0, 0
			while len(to_visita) != 0 :
				isDiG, to_visita, visiteda = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = True)
				compteura += 1

			while len(to_visitb) != 0 :
				isDiG, to_visitb, visitedb = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = False)
				compteurb += 1
			print "PATHS CASE 1 : ", compteura, "LOOPS DONE FORWARD AND", compteurb, "LOOPS DONE BACKWARDS"

			fichier.write("Analyse lexicale pour : ")
			fichier.write(info.encode('utf-8'))
			fichier.write("\n Départ et Arrivée trouvées - Rétropropagation Avant et Arrière \n \n")
			print "Analyse lexicale réussie"
			return (fineG,noDiG,isDiG,1,depart,arrive)

		else :
			n = list(noDiG.nodes)
			first_nodes = []
			for k in range (len(n)):
				if nx.degree(noDiG,n[k]) == 1:
					first_nodes.append( int(n[k]) )
			print "NOMBRE FIRST NODES = " + str(len(first_nodes)), "\t", first_nodes
			if (id_dep != None):

				to_visit, visited = [id_dep], [id_dep]
				compteur = 0
				while len(to_visit) != 0 :
					isDiG, to_visit, visited = retropropogation(noDiG,isDiG,to_visit,visited,info,type_mobility,forward = True)
					compteur += 1
				print "PATHS CASE 2 : ", compteur, "LOOPS DONE FORWARD"

				fichier.write("Analyse lexicale pour : ")
				fichier.write(info.encode('utf-8'))
				fichier.write("\n Départ présent seulement \n \n")
				print "Analyse potentiellement partielle"
				return (fineG,noDiG,isDiG,2,depart,arrive)

			elif (id_arr != None):

				to_visit, visited = [id_arr], [id_arr]
				compteur = 0
				while len(to_visit) != 0 :
					isDiG, to_visit, visited = retropropogation(noDiG,isDiG,to_visit,visited,info,type_mobility,forward = False)
					compteur += 1
				print "PATHS CASE 3 : ", compteur, "LOOPS DONE FORWARD"

				fichier.write("Analyse lexicale pour : ")
				fichier.write(info.encode('utf-8'))
				fichier.write("\n Terminus présent seulement \n \n")
				print "Analyse potentiellement partielle"
				return (fineG,noDiG,isDiG,3,depart,arrive)

			else :
				if (id_dep_iso != None):
					noDig_Edges = list(noDiG.edges)
					if len(noDig_Edges) == 0: 
						fichier.write("Analyse lexicale pour : ")
						fichier.write(info.encode('utf-8'))
						fichier.write("\n Départ présent mais aucun lien dans la relation \n \n")
						print "Problème d'analyse lexicale : relation sans liens"
						return (fineG,noDiG,isDiG,0,depart,arrive)
					else :
						node_info = stations[id_dep_iso]
						s_point = Point([node_info['coords'][0],node_info['coords'][1]])
						nearestCouple = {}
						for p in range (len(noDig_Edges)):
							linestring = geojson.LineString([(noDiG.nodes[noDig_Edges[p][0]]['longitude'],noDiG.nodes[noDig_Edges[p][0]]['latitude']) , (noDiG.nodes[noDig_Edges[p][1]]['longitude'],noDiG.nodes[noDig_Edges[p][1]]['latitude'])])
							feature = geojson.Feature(geometry=linestring, properties={"node1": noDig_Edges[p][0] ,"node2": noDig_Edges[p][1]}) 
							candidate = geojson.dumps(feature)
							line = json.loads(candidate)
							nearestCouple[s_point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
						proche_Edge = min(nearestCouple.keys())

						R = linkNode_OSM(noDiG,id_dep_iso,nearestCouple[proche_Edge],bus = True)
						noDiG, new_node = R[0], R[1]
						isDiG.add_node(int(new_node), ligne = info)
						fineG.add_node(int(new_node), ligne = info)
						new_node_attributes = {new_node : noDiG.nodes[new_node]}
						nx.set_node_attributes(isDiG,new_node_attributes)
						nx.set_node_attributes(fineG,new_node_attributes)
						time = time_travelling(noDiG.nodes[id_dep_iso]['longitude'],noDiG.nodes[new_node]['longitude'],noDiG.nodes[id_dep_iso]['latitude'],noDiG.nodes[new_node]['latitude'],type_mobility)
						
						#noDiG.add_edge(id_dep_iso,new_node,ligne = info, type_mobility=type_mobility, time_travel=time )

						to_visit = [new_node]
						visited = [new_node]
						compteur = 0
						while len(to_visit) != 0 :
							isDiG, to_visit, visited = retropropogation(noDiG,isDiG,to_visit,visited,info,type_mobility,forward = True)
							compteur += 1
						print compteur, "LOOPS DONE"

						fichier.write("Analyse lexicale pour : ")
						fichier.write(info.encode('utf-8'))
						fichier.write("\n Départ présent mais isolé, méthode de rétropropagation \n \n")
						print "Analyse potentiellement partielle"
						return (fineG,noDiG,isDiG,4,depart,arrive)

				elif (id_arr_iso != None):
					noDig_Edges = list(noDiG.edges)
					if len(noDig_Edges) == 0: 
						fichier.write("Analyse lexicale pour : ")
						fichier.write(info.encode('utf-8'))
						fichier.write("\n Arrivée présente mais aucun lien dans la relation \n \n")
						print "Problème d'analyse lexicale : relation sans liens"
						return (fineG,noDiG,isDiG,0,depart,arrive)
					else :
						node_info = stations[id_arr_iso]
						s_point = Point([node_info['coords'][0],node_info['coords'][1]])
						nearestCouple = {}
						for p in range (len(noDig_Edges)):
							linestring = geojson.LineString([(noDiG.nodes[noDig_Edges[p][0]]['longitude'],noDiG.nodes[noDig_Edges[p][0]]['latitude']) , (noDiG.nodes[noDig_Edges[p][1]]['longitude'],noDiG.nodes[noDig_Edges[p][1]]['latitude'])])
							feature = geojson.Feature(geometry=linestring, properties={"node1": noDig_Edges[p][0] ,"node2": noDig_Edges[p][1]}) 
							candidate = geojson.dumps(feature)
							line = json.loads(candidate)
							nearestCouple[s_point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
						proche_Edge = min(nearestCouple.keys())

						R = linkNode_OSM(noDiG,id_arr_iso,nearestCouple[proche_Edge],bus = True)
						noDiG, new_node = R[0], R[1]
						isDiG.add_node(int(new_node), ligne = info)
						fineG.add_node(int(new_node), ligne = info)
						new_node_attributes = {new_node : noDiG.nodes[new_node]}
						nx.set_node_attributes(isDiG,new_node_attributes)
						nx.set_node_attributes(fineG,new_node_attributes)
						time = time_travelling(noDiG.nodes[id_arr_iso]['longitude'],noDiG.nodes[new_node]['longitude'],noDiG.nodes[id_arr_iso]['latitude'],noDiG.nodes[new_node]['latitude'],type_mobility)
						
						#noDiG.add_edge(id_arr_iso,new_node,ligne = info, type_mobility=type_mobility, time_travel=time )

						to_visit = [new_node]
						visited = [new_node]
						compteur = 0
						while len(to_visit) != 0 :
							isDiG, to_visit, visited = retropropogation(noDiG,isDiG,to_visit,visited,info,type_mobility,forward = False)
							compteur += 1
						print compteur, "LOOPS DONE"

						fichier.write("Analyse lexicale pour : ")
						fichier.write(info.encode('utf-8'))
						fichier.write("\n Arrivée présente mais isolée , méthode de rétropropagation \n \n")
						print "Analyse potentiellement partielle"
						return (fineG,noDiG,isDiG,4,depart,arrive)
				else :
					fichier.write("Analyse lexicale pour : ")
					fichier.write(info.encode('utf-8'))
					fichier.write("\n Aucun départ et arrivée détectée \n \n")
					print "Problème d'analyse lexicale"
					return (fineG,noDiG,isDiG,0,depart,arrive)
	else:
		fichier.write("Analyse lexicale pour : ")
		fichier.write(info.encode('utf-8'))
		fichier.write("\n Le nom ne permet pas l'analyse \n \n")
		print "Problème d'analyse lexicale"
		return (fineG,noDiG,isDiG,0,None,None)		

def analyse_lexicogeographique(fineG,noDiG,isDiG,info,stations,fichier,ways_in_relation, departure, arrival, type_mobility = 'Unknown'):
	type_mobility = type_mobility.capitalize()
	distances = {}
	n = list(noDiG.nodes)
	first_nodes = []

	for k in range (len(n)):
		if nx.degree(noDiG,n[k]) == 1:
			first_nodes.append( int(n[k]) )
	print "NOMBRE FIRST NODES = " + str(len(first_nodes)), "\t", first_nodes, [ nx.degree(noDiG,first_nodes[k]) for k in range (len(first_nodes)) ]
	
	d,a = None, None

	if departure != None and arrival != None :

		for key,value in stations.items() :
			if 'name' in value :
				d = key if (departure in value['name']) or (value['name'] in departure) else d
				a = key if (arrival in value['name']) or (value['name'] in arrival) else a
			else :
				continue
		print d, a

	if d != None and a != None :
		if len(first_nodes) == 2 :
			o_Point = Point([stations[d]['coords'][0],stations[d]['coords'][1]])

			one_point = Point( [ noDiG.nodes[first_nodes[0]]['longitude'], noDiG.nodes[first_nodes[0]]['latitude'] ] )
			two_point = Point( [ noDiG.nodes[first_nodes[1]]['longitude'], noDiG.nodes[first_nodes[1]]['latitude'] ] )

			distance_to_one = o_Point.distance(one_point)
			distance_to_two = o_Point.distance(two_point)

			ensemble = { o_Point.distance(one_point) : first_nodes[0] , o_Point.distance(two_point) : first_nodes[1] }

			selected_d = ensemble[min(ensemble.keys())]
			selected_a = ensemble[max(ensemble.keys())]

			to_visita, visiteda, to_visitb, visitedb = [selected_d], [selected_d], [selected_a], [selected_a]
			compteura, compteurb = 0, 0
			while len(to_visita) != 0 :
				isDiG, to_visita, visiteda = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = True, details = False)
				compteura += 1

			while len(to_visitb) != 0 :
				isDiG, to_visitb, visitedb = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = False, details = False)
				compteurb += 1
			print "GEOLEXICAL CASE 1 : ", compteura, "LOOPS DONE FORWARD AND", compteurb, "LOOPS DONE BACKWARDS"

			return (fineG,noDiG,isDiG,9)

		else :
			d_Point = Point([stations[d]['coords'][0],stations[d]['coords'][1]])
			a_Point = Point([stations[a]['coords'][0],stations[a]['coords'][1]])

			d_distances, a_distances = {}, {}

			for element in n :
				o_Point = Point( [ noDiG.nodes[ element ]['longitude'], noDiG.nodes[ element ]['latitude'] ]  )

				d_distances[d_Point.distance(o_Point)] = element
				a_distances[a_Point.distance(o_Point)] = element

			selected_d = d_distances[min(d_distances.keys())]
			selected_a = a_distances[min(a_distances.keys())]

			to_visita, visiteda, to_visitb, visitedb = [selected_d], [selected_d], [selected_a], [selected_a]
			compteura, compteurb = 0, 0
			while len(to_visita) != 0 :
				isDiG, to_visita, visiteda = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = True, details = False)
				compteura += 1

			while len(to_visitb) != 0 :
				isDiG, to_visitb, visitedb = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = False, details = False)
				compteurb += 1
			print "GEOLEXICAL CASE 2 : ", compteura, "LOOPS DONE FORWARD AND", compteurb, "LOOPS DONE BACKWARD"

			return (fineG,noDiG,isDiG,8)

	elif d != None or a != None :

		forward = True if d != None else False
		text = "FORWARD" if forward else "BACKWARD"
		node_on = d if d != None else a 

		d_Point = Point([stations[node_on]['coords'][0],stations[node_on]['coords'][1]])

		d_distances = {}

		for element in n :
			o_Point = Point( [ noDiG.nodes[ element ]['longitude'], noDiG.nodes[ element ]['latitude'] ]  )

			d_distances[d_Point.distance(o_Point)] = element

		selected_d = d_distances[min(d_distances.keys())]

		to_visita, visiteda = [selected_d], [selected_d]
		compteura, compteurb = 0, 0
		while len(to_visita) != 0 :
			isDiG, to_visita, visiteda = retropropogation(noDiG,isDiG,to_visita,visiteda,info,type_mobility,forward = forward, details = False)
			compteura += 1

		print "GEOLEXICAL CASE 3 : ", compteura, "LOOPS DONE", text, "FROM", selected_d

		return (fineG,noDiG,isDiG,7)		


	elif len(first_nodes) != 0 :
		tentative_reussie = False
		for k in range (len(first_nodes)) :
			if nx.degree(noDiG, int(first_nodes[k])) != 0 :
				node_info = noDiG.nodes[first_nodes[k]]
				s_point = Point(node_info['longitude'],node_info['latitude'])
				nearestStation = {}

				if stations != {}:
					for key,value in (stations.items()):
						o_Point = Point([value['coords'][0],value['coords'][1]])
						calcul_distance = s_point.distance(o_Point)
						distances[s_point.distance(o_Point)] = key
						#if 'name' in value :
						#	print value['name'], calcul_distance
						#else :
						#	print calcul_distance
					
					proche_Station = min(distances.keys())
					eloign_Station = max(distances.keys())

					# CRITERIA
						# NAME STATION
					name_in_station = ('name' in stations[distances[proche_Station]]) and ('name' in stations[distances[eloign_Station]])

					if distances[proche_Station] != distances[eloign_Station] :
						if name_in_station :
							print "Création de ligne entre", stations[distances[proche_Station]], " et ", stations[distances[eloign_Station]]
						else :
							print "Création de ligne entre", distances[proche_Station] , " et ", distances[eloign_Station]
						pivot_node = first_nodes[k]
						ephemerGraph = nx.Graph()
						visited_ways = []
						for p in range (len(ways_in_relation)) :
							for key,value in ways_in_relation.items():
								way_nodes = value[0]
								way_tages = value[1]
								if key not in visited_ways :
									if pivot_node in way_nodes :

										if ('oneway' in way_tages) and (way_tages['oneway'] == 'yes') :
											for q in range (1,len(way_nodes)) :
												time = time_travelling(noDiG.nodes[way_nodes[q-1]]['longitude'],noDiG.nodes[way_nodes[q]]['longitude'],noDiG.nodes[way_nodes[q-1]]['latitude'],noDiG.nodes[way_nodes[q]]['latitude'],type_mobility)
												isDiG.add_edge( way_nodes[q-1],way_nodes[q], ligne = info, type_mobility=type_mobility , level_analysis = 2, time_travel=time  )
												ephemerGraph.add_edge( way_nodes[q-1],way_nodes[q], ligne = info, type_mobility=type_mobility , level_analysis = 2  )

										else :
											for q in range (1,len(way_nodes)) :
												time = time_travelling(noDiG.nodes[way_nodes[q-1]]['longitude'],noDiG.nodes[way_nodes[q]]['longitude'],noDiG.nodes[way_nodes[q-1]]['latitude'],noDiG.nodes[way_nodes[q]]['latitude'],type_mobility)
												isDiG.add_edge( way_nodes[q-1],way_nodes[q], ligne = info, type_mobility=type_mobility , level_analysis = 2 , time_travel=time  )
												isDiG.add_edge( way_nodes[q],way_nodes[q-1], ligne = info, type_mobility=type_mobility , level_analysis = 2 , time_travel=time  )
												ephemerGraph.add_edge( way_nodes[q-1],way_nodes[q], ligne = info, type_mobility=type_mobility , level_analysis = 2  )
										
										e_nodes = list(ephemerGraph.nodes)
										visited_ways.append(key)
										degrees = [nx.degree(ephemerGraph,e_nodes[k]) for k in range ((len(e_nodes)))]
										for q in range (len(degrees)) :
											if degrees[q] == 1 :
												if e_nodes[q] == pivot_node :
													continue
												else :
													pivot_node = e_nodes[q]
									else :
										continue
								else :
									continue
						tentative_reussie = True
					else :
						continue
				else :
					continue
			else : 
				continue
		if tentative_reussie :
			print "Analyse Geolexicale effectuée. Attention, le graphe peut ne pas représenter les directions réelles"
			return (fineG,noDiG,isDiG,1)
		else :
			print "Tentative échouée"
			return (fineG,noDiG,isDiG,0)		

	else :
		print "Aucun noeud de degré 1 : le graphe a soit aucun lien soit est un cycle"
		return (fineG,noDiG,isDiG,0)

def redirection_par_defaut (fineG,noDiG,isDiG,info,stations,fichier,ways_in_relation, type_mobility = 'Unknown'):
	type_mobility = type_mobility.capitalize()
	couples_distances = {}
	n = list(noDiG.nodes)
	first_nodes = []
	for k in range (len(n)):
		if nx.degree(noDiG,n[k]) == 1:
			first_nodes.append( int(n[k]) )
	print "NOMBRE FIRST NODES = " + str(len(first_nodes)), "\t", first_nodes

	if len(first_nodes) > 0 :
		for k in range (len(first_nodes)) : 

			for p in range (len(ways_in_relation)) :
				for key,value in ways_in_relation.items():
					way_nodes = value[0]
					way_tages = value[1]
					
					if ('oneway' in way_tages) and (way_tages['oneway'] == 'yes') :
						for q in range (1,len(way_nodes)) :
							#print noDiG.nodes[way_nodes[q-1]],noDiG.nodes[way_nodes[q]]
							time = time_travelling(noDiG.nodes[way_nodes[q-1]]['longitude'],noDiG.nodes[way_nodes[q]]['longitude'],noDiG.nodes[way_nodes[q-1]]['latitude'],noDiG.nodes[way_nodes[q]]['latitude'],type_mobility)
							isDiG.add_edge( way_nodes[q-1],way_nodes[q], ligne = info, type_mobility=type_mobility , level_analysis = 2 ,time_travel=time )

					else :
						for q in range (1,len(way_nodes)) :
							time = time_travelling(noDiG.nodes[way_nodes[q-1]]['longitude'],noDiG.nodes[way_nodes[q]]['longitude'],noDiG.nodes[way_nodes[q-1]]['latitude'],noDiG.nodes[way_nodes[q]]['latitude'],type_mobility)
							isDiG.add_edge( way_nodes[q-1],way_nodes[q], ligne = info, type_mobility=type_mobility , level_analysis = 2 ,time_travel=time )
							isDiG.add_edge( way_nodes[q],way_nodes[q-1], ligne = info, type_mobility=type_mobility , level_analysis = 2 ,time_travel=time )
					
		fichier.write("Default redirection for : ")
		fichier.write(info.encode('utf-8'))
		fichier.write("\n \n")
		print "Redirection par défaut effectuée"
		return (fineG,noDiG,isDiG)

	elif len(noDiG.edges)==0 :
		fichier.write("Il n'y a pas de liens dans le graphe, il sera traité à part (Euler) ")
		fichier.write(info.encode('utf-8'))
		fichier.write("-pass-")
		fichier.write("\n \n")
		return 0	

	else :
		fichier.write("Default redirection failed (no first nodes) for : ")
		fichier.write(info.encode('utf-8'))
		fichier.write("Drawing default edges")
		fichier.write("\n \n")
		print "Default redirection failed (no first nodes), drawing default edges"
		ee = list(noDiG.edges)
		for k in range (len(ee)):
			time = time_travelling(noDiG.nodes[ee[k][0]]['longitude'],noDiG.nodes[ee[k][1]]['longitude'],noDiG.nodes[ee[k][0]]['latitude'],noDiG.nodes[ee[k][1]]['latitude'],type_mobility)
			isDiG.add_edge( ee[k][0],ee[k][1], ligne = info, type_mobility=type_mobility , level_analysis = 9 ,time_travel=time )
			isDiG.add_edge( ee[k][1],ee[k][0], ligne = info, type_mobility=type_mobility , level_analysis = 9 ,time_travel=time )			
		return (fineG,noDiG,isDiG)		


def trace_cycle (fineG,noDiG,isDiG,info,stations,fichier, type_mobility = 'Unknown'):
	type_mobility = type_mobility.capitalize()
	cycles = list(nx.cycle_basis(noDiG))
	nb_cycles = len(cycles)
	if len(cycles) == 0 :
		fichier.write("No cycles found for : ")
		fichier.write(info.encode('utf-8'))
		fichier.write("\n \n")
		print "No cycle found"
		return (fineG,noDiG,isDiG)
	else :
		for k in range (nb_cycles):
			le_cycle = cycles[k]
			for p in range (1,len(le_cycle)) :
				if (isDiG.has_edge(le_cycle[p-1],le_cycle[p])) or (isDiG.has_edge(le_cycle[p],le_cycle[p-1])) :
					continue
				else :
					time = time_travelling(noDiG.nodes[le_cycle[p-1]]['longitude'],noDiG.nodes[le_cycle[p]]['longitude'],noDiG.nodes[le_cycle[p-1]]['latitude'],noDiG.nodes[le_cycle[p]]['latitude'],type_mobility)
					isDiG.add_edge(le_cycle[p-1],le_cycle[p], ligne = info, type_mobility=type_mobility , level_analysis = 3 , time_travel=time )
			
			if (isDiG.has_edge(le_cycle[-1],le_cycle[0])):			
				time = time_travelling(noDiG.nodes[le_cycle[-1]]['longitude'],noDiG.nodes[le_cycle[0]]['longitude'],noDiG.nodes[le_cycle[-1]]['latitude'],noDiG.nodes[le_cycle[0]]['latitude'],type_mobility)
				isDiG.add_edge(le_cycle[-1],le_cycle[0], ligne = info, type_mobility=type_mobility , level_analysis = 3 , time_travel=time )

		fichier.write(str(nb_cycles).encode('utf-8'))
		fichier.write("Cycles drawn for ")
		fichier.write(info.encode('utf-8'))
		fichier.write("\n \n")
		print nb_cycles, "cycles found for this line"
		return (fineG,noDiG,isDiG)		


def mesureLevenshtein (motA, motB):
	d = [[0 for k in range (len(motB)+1)] for j in range (len(motA)+1)]
	for i in range (len(motA)+1):
		d[i][0] = i
	for j in range (len(motB)+1):
		d[0][j] = j

	for i in range (len(motA)):
		for j in range(len(motB)):
			if motA[i] == motB[j] :
				cout = 0
			else :
				cout = 1
			d[i+1][j+1] = min( d[i][j+1] + 1 , d[i+1][j]+1, d[i][j] + cout)

	return d[len(motA)][len(motB)]

def replacer_A (isDiG, Gfinal, info_name):
	injective = {}
	nodes = list( isDiG.nodes )
	edges = list( isDiG.edges )
	listn = []
	liste = []
	for k in range ( len(nodes) ):
		txt = str(isDiG.nodes[nodes[k]]['longitude']).encode('utf-8') + str(isDiG.nodes[nodes[k]]['latitude']).encode('utf-8') + info_name
		txt2 = txt.encode('ascii','ignore')
		#print txt2, type(txt2)
		aff = int(hashlib.md5(txt2).hexdigest(), 16)
		injective[nodes[k]] = aff
		attributes = isDiG.nodes[nodes[k]]
		attributes['original_osmid'] = str(nodes[k])
		listn.append( (aff,attributes) )
	Gfinal.add_nodes_from( listn )

	for k in range ( len(edges) ):
		liste.append( (injective[edges[k][0]], injective[edges[k][1]], isDiG[ edges[k][0] ][ edges[k][1] ]) )
	#print "On ajoute : ", len(liste), " liens"
	Gfinal.add_edges_from( liste )
	#print "Graphe final", len(list(Gfinal.edges)), " liens "
	return Gfinal

def replacer_B (isDiG, Gfinal, info_name):
	edges = list( isDiG.edges )
	liste = []
	for k in range ( len(edges) ):
		liste.append( (edges[k][0], edges[k][1],isDiG[ edges[k][0] ][ edges[k][1] ]) )
	#print "On ajoute : ", len(liste), " liens"
	Gfinal.add_edges_from( liste )
	#print "Graphe final", len(list(Gfinal.edges)), " liens "
	return Gfinal


def eulerian (graph, nodes, info_name, rTreefile, dict_of_edge_id, csvfile) :
	#1st step : determine the first and last station by distance 
	mean_distances = {}
	#print nodes
	for key,value in nodes.items() :
		s_point = Point([value['coords'][0],value['coords'][1]])
		sum_distances = 0
		for pey, palue in nodes.items():
			p_point = Point([palue['coords'][0],palue['coords'][1]])
			sum_distances += s_point.distance(p_point)

		mean_distances[float(sum_distances)/float(len(nodes))] = key

	the_first_node = min(mean_distances.values())

	#2nd step : make accessible the nodes in the road graph
	nds = {} # key : road node / value : transportation node
	sdn = {} # value : road node / key : transportation node
	for key,value in nodes.items() :
		# If the node is already in the graph, then it's a transportation node
		if key in list(graph.nodes) :
			s_point = Point([value['coords'][0],value['coords'][1]])
			y_add = int(hashlib.md5(s_point.wkt).hexdigest(), 16)
			graph.add_node(y_add, longitude = value['coords'][0], latitude = value['coords'][1], utilisation = 'Undefined', ligne = info_name)
			nds[key] = y_add
			sdn[y_add] = key
		else :
			graph.add_node(key, longitude = value['coords'][0], latitude = value['coords'][1], utilisation = 'Undefined', ligne = info_name)
			R = linkNode_OSM_Rtree(graph, key, dict_of_edge_id, diriged = True, rtreefile=rTreefile, csvfile=csvfile)
			
			if type(R) == int :
				print "RTREE LINK ERROR"
				continue
			graph, new_node, dict_of_edge_id, rTreefile= R[0], R[1], R[4], R[5]
			time = time_travelling(graph.nodes[new_node]['longitude'],graph.nodes[key]['longitude'],graph.nodes[new_node]['latitude'],graph.nodes[key]['latitude'], 'pedestrian')
			graph.add_edge(new_node,key,type_mobility = 'Pedestrian_Xxx-Road', level_analysis=-1, time_travel = time)
			graph.add_edge(key,new_node,type_mobility = 'Pedestrian_Xxx-Road', level_analysis=-1, time_travel = time)
			nds[new_node] = key
			sdn[key] = new_node


	#3rd step : calculate shortest length and apply
	#print the_first_node
	try :
		visited_nodes = [ nds[the_first_node] if the_first_node in nds else sdn[the_first_node] ]
		for k in range (len(nodes)) :
			for key, value in nodes.items():
				if key in visited_nodes :
					continue
				else :
					visited_nodes.append(key)
					distances = {}
					for pey, palue in nds.items():
						distances[nx.shortest_path_length(graph, source = visited_nodes[-1], target = pey, weight= 'time_travel')] = pey

					nearest = min(distances.values())
					the_way = nx.shortest_path(graph, source = visited_nodes[-1], target = nearest, weight= 'time_travel')
					phe_way = [visited_nodes[-1]]
					for p in range (1,len(the_way)) :
						if p == 1 :
							s_point = Point([graph.nodes[the_way[p]]['longitude'],graph.nodes[the_way[p]]['latitude']])
							y_add = int(hashlib.md5(s_point.wkt).hexdigest(), 16)
							time = time_travelling(graph.nodes[the_way[p]]['longitude'],graph.nodes[visited_nodes[-1]]['longitude'],graph.nodes[the_way[p]]['latitude'],graph.nodes[visited_nodes[-1]]['latitude'], 'bus')
							graph.add_node(y_add, longitude = graph.nodes[the_way[p]]['longitude'], latitude = graph.nodes[the_way[p]]['latitude'], utilisation = 'Undefined', ligne = info_name)						
							graph.add_edge(visited_nodes[-1],y_add,type_mobility = 'Undefined', level_analysis=-1, time_travel = time, ligne = info_name)
							phe_way.append(y_add)

						elif p == len(the_way)-1 :
							time = time_travelling(graph.nodes[the_way[p-1]]['longitude'],graph.nodes[visited_nodes[-1]]['longitude'],graph.nodes[the_way[p-1]]['latitude'],graph.nodes[visited_nodes[-1]]['latitude'], 'bus')						
							graph.add_edge(the_way[p-1],nearest,type_mobility = 'Undefined', level_analysis=-1, time_travel = time, ligne = info_name)

						else :
							s_point = Point([graph.nodes[the_way[p]]['longitude'],graph.nodes[the_way[p]]['latitude']])
							y_add = int(hashlib.md5(s_point.wkt).hexdigest(), 16)
							time = time_travelling(graph.nodes[the_way[p]]['longitude'],graph.nodes[visited_nodes[-1]]['longitude'],graph.nodes[the_way[p]]['latitude'],graph.nodes[visited_nodes[-1]]['latitude'], 'bus')
							graph.add_node(y_add, longitude = graph.nodes[the_way[p]]['longitude'], latitude = graph.nodes[the_way[p]]['latitude'], utilisation = 'Undefined', ligne = info_name)						
							graph.add_edge(phe_way[-1],y_add,type_mobility = 'Undefined', level_analysis=-1, time_travel = time, ligne = info_name)
							phe_way.append(y_add)

	except Exception, e :
		print "TREATMENT ERROR FOR : ", info_name
		print e		


	return graph, dict_of_edge_id, rTreefile


def road_support (osmid, tags, refs,nodes,r_graph,f_graph = None):
	highway = tags['highway']
	bicycle = False
	footway = True
	oneway = False
	lanes = 1
	level = -1
	type_mobility = 'Road'
	
	if (highway == 'elevator') or (highway == 'steps') or (highway == 'platform') or (highway == 'bus_stop') or (highway == 'platform'):
		#print "NO TREATMENT FOR ", osmid
		return (r_graph,f_graph)

	# Update BICYCLING information using specific tag (priority) or 'highway' tag
	if 'bicycle' in tags:
		if tags['bicycle'] == 'yes' or tags['bicycle'] == 'designated' :
			bicycle = True
			#type_mobility = 'Bicycle'
		else :
			bicycle = False
	elif highway == 'cycleway' or highway == 'cyleway' :
		bicycle = True
		type_mobility = 'Bicycle'
	else:
		bicycle = False

	# Update PEDESTRIAN information using specific tag (priority) or 'highway' tag
	if 'foot' in tags:
		if tags['foot'] == 'yes' :
			footway = True
			type_mobility = 'Pedestrian'
		else :
			footway = False 
	elif highway == 'pedestrian' or highway == 'footway':
		footway = True
		type_mobility = 'Pedestrian'
	else:
		footway = False

	if 'oneway' in tags:
		oneway = True if tags['oneway'] == 'yes' else False
	
	# update LANE COUNT information from the tag 'lanes'
	if 'lanes' in tags:
		lanes = tags['lanes']
		m = re.search('\D', lanes)
		try:
			if m:
				lanes = int(lanes[:m.start()])
			else:
				lanes = int(lanes)
		except ValueError, e:
			lanes = 1
			print 'lanes tag value error for',tags['lanes'],'for osmid',osmid,'default to 1'
	
	#TODO add sidewalk information

	# update HIGHWAY information from the tag 'highway'
	# if highway tag is not osm compliant, highway is defaulted to 'unclassified'
	try:
		highway.encode('ascii')
	except UnicodeDecodeError:
		highway = 'unclassified'

	for levelItem in levels['levels']:
		key, values = levelItem.keys()[0], levelItem.values()[0]
		if str(highway).lower() in values:
			level = key
	
	# if the level is unknow you might want to include it in the level file (roadTypes.py)
	# it oftens comes from miswritten osm tag
	if level == -1:
		print 'highway tag',highway,'unknow for osmid',osmid,'default to level 3'
		level = 3

	if oneway :
		for i in range(1, len(refs)):
			r_graph.add_node(refs[i-1], longitude = nodes[refs[i-1]]['coords'][0], latitude = nodes[refs[i-1]]['coords'][1], utilisation = 'Circulation')
			r_graph.add_node(refs[i], longitude = nodes[refs[i]]['coords'][0], latitude = nodes[refs[i]]['coords'][1], utilisation = 'Circulation')	
			x1,x2,y1,y2 = nodes[refs[i-1]]['coords'][0], nodes[refs[i]]['coords'][0], nodes[refs[i-1]]['coords'][1], nodes[refs[i]]['coords'][1]	
			time = time_travelling(x1,x2,y1,y2,'pedestrian')			
			r_graph.add_edge(refs[i-1], refs[i], osmid=osmid, highway=str(highway), level=int(level), lanes=lanes, oneway=oneway, footway=footway, bicycle=bicycle, type_mobility=type_mobility, time_travel=time)

			if int(level)<7:
				r_graph.add_edge(refs[i], refs[i-1], osmid=osmid, highway=str(highway), level=int(level), lanes=lanes, oneway=oneway, footway=footway, bicycle=bicycle, type_mobility='Sidewalk', time_travel=time)

		return (r_graph,f_graph)
	else :
		for i in range(1, len(refs)):
			r_graph.add_node(refs[i-1], longitude = nodes[refs[i-1]]['coords'][0], latitude = nodes[refs[i-1]]['coords'][1], utilisation = 'Circulation')
			r_graph.add_node(refs[i], longitude = nodes[refs[i]]['coords'][0], latitude = nodes[refs[i]]['coords'][1], utilisation = 'Circulation')
			x1,x2,y1,y2 = nodes[refs[i-1]]['coords'][0], nodes[refs[i]]['coords'][0], nodes[refs[i-1]]['coords'][1], nodes[refs[i]]['coords'][1]	
			time = time_travelling(x1,x2,y1,y2,'pedestrian')
			r_graph.add_edge(refs[i-1], refs[i], osmid=osmid, highway=str(highway), level=int(level), lanes=lanes, oneway=oneway, footway=footway, bicycle=bicycle, type_mobility=type_mobility, time_travel=time)
			r_graph.add_edge(refs[i], refs[i-1], osmid=osmid, highway=str(highway), level=int(level), lanes=lanes, oneway=oneway, footway=footway, bicycle=bicycle, type_mobility=type_mobility, time_travel=time)

		return (r_graph,f_graph)

