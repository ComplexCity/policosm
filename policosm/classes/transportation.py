#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
In progress since June 2018 in ComplexCity Lab

@author: github.com/fpfaende

Object :
	The transportation module which transforms xml data into mobility graph

Parameters :
	OSM File (xml required, pbf not ready yet)
	[Functions with POLICOSM SAX PARSER (see policosmsax.py)]

How it works :
	N/A

Returns :
	A Transportation object which graph can be called

'''
import hashlib
import json

import geojson
import networkx as nx
import osmium
from shapely.geometry import LineString, Point

import policosm.functions.transportationLineAnalysis as tla
from policosm.geoNetworks.linkNewNodes import linkNode_OSM


class Transportation(osmium.SimpleHandler):
	def __init__(self):
		osmium.SimpleHandler.__init__(self)
		self.coords = {}
		self.nodes = {}
		self.ways = {}
		self.relations = {}
		self.to_eulerian = {}
		self.graph = nx.MultiDiGraph()
		self.r_graph = nx.MultiDiGraph()
		self.geolexical = {}
		self.nodes_residue = 0
		self.stations = {}
		self.boundary = nx.MultiDiGraph()
	
	def getGraph(self):
		return self.graph

	def get_Roads(self):
		return self.r_graph

	def get_Bounds(self):
		return self.boundary

	def draw_roads(self):
		print ("ROADS DRAWING")
		c , t , p = 1, len(self.ways), 0.25
		for key, value in self.ways.items():
			if (float(c)/float(t)) > p or c==t-1 :
				print (p*100, "%", " complete")
				p+=0.25

			if 'highway' in value['tags']:
				R = tla.road_support(key, value['tags'], value['nds'],self.nodes,self.r_graph)
				self.r_graph = R[0]
				c+=1
			else :
				c+=1
				continue

	def draw_bounds(self) :

		count = 0

		for keyOsmid, relValues in self.relations.items() :
			
			tags, members = relValues['tags'], relValues['membs']

			if 'admin_level' in tags and tags['admin_level'] == '8' :

				ways_in_relation = {}

				for elem in range (len(members)):
					osmid, osmType,osmDetail = members[elem]['ref'], members[elem]['type'], members[elem]['role']

					if osmType == 'way':
						if osmid in self.ways : 
							way_nodes = self.ways[osmid]['nds']
							way_tag = self.ways[osmid]['tags']

							ways_in_relation[osmid] = {'nds' : way_nodes, 'tags' : way_tag}
							
				for key,value in ways_in_relation.items() :

					tags = value['tags']
					nds = value['nds']

					list_of_nodes = nds
					constructible = []
					for nodei in list_of_nodes :

						the_node = int(nodei)
						lon, lat = self.nodes[the_node]['coords'][0], self.nodes[the_node]['coords'][1]
						aff = int(hashlib.md5(str(lon) + str(lat) + str(the_node) + "BOUND NUMBER" + str(count)).hexdigest(), 16)
						if aff not in list(self.boundary.nodes) :
							self.boundary.add_node(aff,original_osmid = str(the_node), longitude=lon, latitude=lat, utilisation="Boundary", color = '#000000')
						constructible.append(aff)

						if the_node == 421488092 :
							print ("HERE", aff)
					#print constructible
					for nodei in range (1,len(constructible)) :
						self.boundary.add_edge( int(constructible[nodei-1]), int(constructible[nodei]), special='Boundary')

					count += 1

			else :
				continue


	def info(self):
		info =  'nodes:' + str(len(self.nodes)) + '\n'
		info += 'ways:' + str(len(self.ways)) + '\n'
		info += 'relations:' + str(len(self.relations)) + '\n'
		return info
	
	def transportation_Analysis (self, lineAnalysis = False, extern_Graph = None):

		if extern_Graph != None :
			self.graph = extern_Graph
	
		fichierCSV = open('data1.csv','w')
		csvData = open('data2.csv','w')

		isDiGraph = nx.DiGraph()
		noDiGraph = nx.Graph()
		default_counter = 1
		fichier = open('notes.txt','w')
		nb_relations, relations_count = len(self.relations),1

		means = ['bus','subway','tram','light_rail']
		list_of_diGraphs = []

		for keyOsmid, relValues in self.relations.items():

			if relations_count < 0 :
				print ("RELATION NUMBER ", relations_count, "SKIPPED")
				relations_count += 1
				continue

			tags, members = relValues['tags'], relValues['membs']

			print ("PROGRESS : ", relations_count, "/", nb_relations)
			# STEP 1 : Determine if the relation is linked to a transportation system and draw the line
			if (('route' in tags) and (tags['route'] in means)) or (('route_master' in tags) and (tags['route_master'] in means)) or (('type' in tags) and ('public_transport' in tags)):
				try :
					mean = tags['route']
				except :
					try :
						mean = tags['route_master']
					except :
						mean = 'stop_area'

				G = tla.elements_du_graphe(self.graph,isDiGraph,noDiGraph,keyOsmid,tags,members, self.nodes, self.ways, self.coords, default_counter, fichierCSV, csvData, self.stations, self.nodes_residue, type_tr = mean)

			else :
				if 'route' in tags:
					print ("The algorithm doesn't process this route : ", tags['route'])
				else :
					print ("The algorithm doesn't process this relation : ", tags)
				print ('\n')
				relations_count += 1
				continue

			if type(G) is int :
				relations_count += 1
				continue
			else :
				if len(G) == 1 : # CASE OF STOP AREA
					self.graph = G[0]
					relations_count += 1
					print ('\n')
					continue
				else :
					self.graph, isDiGraph, noDiGraph, ways_in_relation, relation_station, relation_platforms, info_name, default_counter, self.stations, self.nodes_residue = G[0], G[1], G[2], G[3], G[4], G[5], G[6], G[7], G[8], G[9]
					print ("STEP 1 COMPLETE , FINAL GRAPH STATE : ", len( list (self.graph.edges)), " EDGES ; ", len( list (self.graph.nodes)), " NODES ")

			# STEP 2 : ORIENTING THE GRAPH
				# On essaye dans un premier temps de déterminer les terminus grâce au nom de ligne
			R = tla.analyse_lexicale(self.graph,noDiGraph,isDiGraph,info_name,relation_station,fichier, tags, type_mobility=mean)
			self.graph, noDiGraph, isDiGraph, res, departure, arrival = R[0], R[1], R[2], R[3], R[4], R[5]

			if res == 0 :
				R = tla.analyse_lexicogeographique(self.graph,noDiGraph,isDiGraph,info_name,relation_station,fichier, ways_in_relation, departure, arrival, type_mobility = mean)
				self.graph, noDiGraph, isDiGraph, res = R[0], R[1], R[2], R[3]

				if res == 0 : 
					R = tla.redirection_par_defaut(self.graph,noDiGraph,isDiGraph,info_name,relation_station,fichier, ways_in_relation, type_mobility = mean)

					if type(R)== int :
						self.to_eulerian[info_name] = relation_station
						relations_count += 1
						continue
					else :
						self.graph, noDiGraph, isDiGraph = R[0], R[1], R[2]
					#fichierCSV.write(info_name.encode('utf-8') + ";" + str("Default") + "\n")
				else :
					#fichierCSV.write(info_name.encode('utf-8') + ";" + str("Level 2") + "\n")
					pass
			else :
				#fichierCSV.write(info_name.encode('utf-8') + ";" + str("Level 1") + "\n")
				pass

			# Tracé des cycles 
			R = tla.trace_cycle(self.graph,noDiGraph,isDiGraph,info_name,relation_station,fichier, type_mobility=mean)
			self.graph, noDiGraph, isDiGraph = R[0], R[1], R[2]
			
			print ("STEP 2 COMPLETE , FINAL GRAPH STATE : ", len( list (self.graph.edges)), " EDGES ; ", len( list (self.graph.nodes)), " NODES ")
			
			# ETAPE 3a : On rajoute les plateformes : simplifiés en noeud centroïde [exclusif bus pour l'instant]
				#Rq : mise à la fin pour éviter les conflits de degré de noeuds			
			if mean in ['bus','light_rail','tram']:
				utiliZation = "Bus Station" if mean == 'bus' else "Tramway Station" if mean == 'tram' else "Light Rail Station" if mean == 'light_rail' else "Undfined Station"
				for key,value in relation_platforms.items() :
					list_of_nodes = value[0]
					longs, latts = [], []
					for nodei in range (len(list_of_nodes)) :
						longs.append(self.nodes[list_of_nodes[nodei]]['coords'][0])
						latts.append(self.nodes[list_of_nodes[nodei]]['coords'][1])
					moy_longs = float(sum(longs)/len(longs))
					moy_latts = float(sum(latts)/len(longs))
					
					s_point = Point(moy_longs,moy_latts)
					adde  = -int(hashlib.md5(s_point.wkt).hexdigest(), 16)
					isDiGraph.add_node(adde,longitude=moy_longs, latitude=moy_latts, nom = value[1] ,utilisation=utiliZation,ligne = info_name)
					self.graph.add_node(adde,longitude=moy_longs, latitude=moy_latts, nom = value[1] ,utilisation=utiliZation,ligne = info_name)

					nearestCouple = {}
					edges = list(isDiGraph.edges)
					for p in range (len(edges)):
						linestring = geojson.LineString([(isDiGraph.nodes[edges[p][0]]['longitude'],isDiGraph.nodes[edges[p][0]]['latitude']) , (isDiGraph.nodes[edges[p][1]]['longitude'],isDiGraph.nodes[edges[p][1]]['latitude'])])
						feature = geojson.Feature(geometry=linestring, properties={"node1": edges[p][0] ,"node2": edges[p][1]}) 
						candidate = geojson.dumps(feature)
						line = json.loads(candidate)
						nearestCouple[s_point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
					if nearestCouple != {} :
						proche_Edge = min(nearestCouple.keys())
						#print proche_Edge
						#print "A", nearestCouple[proche_Edge]
						if proche_Edge < 0.0001 :
							R = linkNode_OSM(isDiGraph,adde,nearestCouple[proche_Edge],diriged = True, bus = True)
							isDiGraph, new_node, u,v = R[0], R[1], R[2], R[3]
							self.graph.add_node(new_node, utilisation='Link Platform_BusLine',ligne = info_name)
							new_node_attributes = {new_node : isDiGraph.nodes[new_node]}
							#print new_node_attributes
							nx.set_node_attributes(self.graph,new_node_attributes)
							use = 'Platform_to_' + str(mean.capitalize())
							waiting_time = tla.waiting_bus_time if mean == 'bus' else tla.waiting_trm_time if (mean == 'tram' or mean == 'light_rail') else tla.waiting_bus_time
							isDiGraph.add_edge(adde,new_node, type_mobility=use, ligne= info_name, time_travel= waiting_time)		# Entry
							isDiGraph.add_edge(new_node,adde, type_mobility=use, ligne= info_name, time_travel= 0) 					# Exit
						else :
							continue
					else :
						continue

				print ("STEP 3 COMPLETE , FINAL GRAPH STATE : ", len( list (self.graph.edges)), " EDGES ; ", len( list (self.graph.nodes)), " NODES ")

			# STEP 4 : On raccorde les stations intermdiaires représentées que par des points
				#Rq : mise à la fin pour éviter les conflits de degré de noeuds
			for key,value in relation_station.items() :
				if isDiGraph.degree[key] == 0 :
					node_to_link = key
					s_point = Point([value['coords'][0],value['coords'][1]])

					nearestCouple = {}
					edges = list(isDiGraph.edges)
					for p in range (len(edges)):
						#print edges[p][0], isDiGraph.nodes[edges[p][0]], edges[p][1], isDiGraph.nodes[edges[p][1]]
						linestring = geojson.LineString([(isDiGraph.nodes[edges[p][0]]['longitude'],isDiGraph.nodes[edges[p][0]]['latitude']) , (isDiGraph.nodes[edges[p][1]]['longitude'],isDiGraph.nodes[edges[p][1]]['latitude'])])
						feature = geojson.Feature(geometry=linestring, properties={"node1": edges[p][0] ,"node2": edges[p][1]}) 
						candidate = geojson.dumps(feature)
						line = json.loads(candidate)
						nearestCouple[s_point.distance(LineString(line['geometry']['coordinates']))]=(line['properties'].values())
					if nearestCouple != {} :
						proche_Edge = min(nearestCouple.keys())
						#print proche_Edge
						#print "A", nearestCouple[proche_Edge]
						if proche_Edge < 0.0001 :
							R = linkNode_OSM(isDiGraph,node_to_link,nearestCouple[proche_Edge],diriged = True, bus = True)
							isDiGraph, new_node, u, v = R[0], R[1], R[2], R[3]
							self.graph.add_node(new_node, utilisation='Link Station_BusLine', ligne = info_name)
							new_node_attributes = {new_node : isDiGraph.nodes[new_node]}
							#print new_node_attributes
							nx.set_node_attributes(self.graph,new_node_attributes)
							if mean in ['bus','light_rail','tram'] :
								use = 'Station_to_' + str(mean.capitalize())
								waiting_time = tla.waiting_bus_time if mean == 'bus' else tla.waiting_trm_time if (mean == 'tram' or mean == 'light_rail') else tla.waiting_bus_time
								isDiGraph.add_edge(node_to_link,new_node, type_mobility=use, ligne= info_name, time_travel= waiting_time)	# Entry
								isDiGraph.add_edge(new_node,node_to_link, type_mobility=use, ligne= info_name, time_travel= 0)				# Exit
							elif mean == 'subway' :
								isDiGraph.add_edge(node_to_link,new_node, type_mobility='Subway_Linked', ligne= info_name, time_travel= tla.waiting_sub_time)
								isDiGraph.add_edge(new_node,node_to_link, type_mobility='Subway_Linked', ligne= info_name, time_travel= 0)							

						else :
							continue
					else :
						continue
				else :
					continue

			print ("STEP 4 COMPLETE , FINAL GRAPH STATE : ", len( list (self.graph.edges)), " EDGES ; ", len( list (self.graph.nodes)), " NODES ")

			nx.set_node_attributes(isDiGraph,self.stations)
			self.stations = {}

			# STEP 4 : ADD INTO THE FINAL GRAPH
			if mean == 'bus' :
				self.graph = tla.replacer_A(isDiGraph, self.graph, info_name)
			else :
				self.graph = tla.replacer_B(isDiGraph, self.graph, info_name)
			print ("STEP 5 COMPLETE , FINAL GRAPH STATE : ", len( list (self.graph.edges)), " EDGES ; ", len( list (self.graph.nodes)), " NODES ")

			print ('\n')

			isDiGraph.clear()
			noDiGraph.clear()
			relations_count += 1

		fichier.close()
		fichierCSV.close()

if __name__ == "__main__":
	print ("Rien")
