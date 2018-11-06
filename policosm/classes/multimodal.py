#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
In progress since June 2018 in ComplexCity Lab

@author: github.com/fpfaende

Object :
	From opendata website (OpenStreetMap), we draw transportation network

Parameters :
	OSM File
	User criterias

Processing method :
	First, the file is parsed
	Then, the transportation graph is drawn 
	Finnaly, we add road network and merge the two graphs into one

Returns :
	Graphe multimodal

'''

import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/alex/Bureau')

import policosm.functions.transportationLineAnalysis as tla
import policosm.geoNetworks.accessible_travelling_zone as acc
import policosm.geoNetworks.draw_isochrone as drw

from imposm.parser import OSMParser
from policosm.classes.roads import Roads
from policosm.functions.getRtree import *
from policosm.geoNetworks.clean import clean
from policosm.extractors.policosmsax import *
from policosm.classes.transportation import *
from policosm.geoNetworks.linkNewNodes import linkNode_OSM_Rtree, nearestEdgeFromPoint

def rescale_esthetic (graph) :

	to_add = {}
	graph_edges = list(graph.edges(keys=True,data=True))

	for element in graph_edges :
		if 'special' in element[3] and element[3]['special'] == 'Boundary' :
			to_add[(element[0],element[1],element[2])] = {'weight':1}
		else :
			to_add[(element[0],element[1],element[2])] = {'weight':0.1}

	nx.set_edge_attributes(graph, to_add)

	return graph


def linkToRoads (tr_Graph,road_Graph,filename,rTree, dict_of_edge_id, csvfile) :

	tr_Utilization = nx.get_node_attributes(tr_Graph,'utilisation')
	r = rTree
	Road_Edges = list(road_Graph.edges)

	for key,value in tr_Utilization.items() :

		if ((value == 'Bus Station') or  (value == 'Tramway Station') or (value == 'Subway Entrance') or (value == 'Created Subway Entrance')) and not( 'rTreeD' in road_Graph.nodes[key]):
			#print "Link to ", key
			node_to_link = key

			if value == 'Created Subway Entrance' :
				R = linkNode_OSM_Rtree(tr_Graph, node_to_link, dict_of_edge_id, diriged = True, details = False, rtreefile=r, csvfile=csvfile)
			else :
				R = linkNode_OSM_Rtree(tr_Graph, node_to_link, dict_of_edge_id, diriged = True, details = False, rtreefile=r, csvfile=csvfile)
			
			if type(R) == int :
				print "RTREE LINK ERROR FOR ", key
				continue

			tr_Graph, new_node = R[0], R[1]
			time = tla.time_travelling(tr_Graph.nodes[new_node]['longitude'],tr_Graph.nodes[node_to_link]['longitude'],tr_Graph.nodes[new_node]['latitude'],tr_Graph.nodes[node_to_link]['latitude'], 'pedestrian')
			to_value = 'Pedestrian_' + value + '-Road'
			tr_Graph.add_edge(new_node,node_to_link,type_mobility = to_value, level_analysis=-1, time_travel = time)
			tr_Graph.add_edge(node_to_link,new_node,type_mobility = to_value, level_analysis=-1, time_travel = time)
			
			if value == 'Created Subway Entrance' :
				print "HERE", key, tr_Graph[key], R[2], R[3], tr_Graph.has_edge(R[2],R[3]), tr_Graph.has_edge(R[3],R[2]), tr_Graph.has_edge(R[2],new_node), tr_Graph.has_edge(new_node,R[3]),tr_Graph.has_edge(R[3],new_node), tr_Graph.has_edge(new_node,R[2])

			dict_of_edge_id, r = R[4], R[5]
		else :
			continue
	return tr_Graph

def cityMobility(filename, transportationGraph = False):

	Mobility_Graph = nx.MultiDiGraph()
	csvfile = open('not_treed_edges.csv','w')

	transportation = Transportation()
	transport_data = je_parse(filename)

	transportation.nodes, transportation.ways, transportation.relations = transport_data[0], transport_data[1], transport_data[2]

	transportation.draw_bounds()
	bounds_Grpah = transportation.get_Bounds()
	
	transportation.transportation_Analysis()
	mobility_Graph = transportation.getGraph()

	if transportationGraph :
		print "WRITING TRANSPORTATION GRAPH"
		nx.write_gexf(mobility_Graph, '/home/alex/Bureau/TransportOnly-toulouse-30-8tr.gexf')
		print "FILE COMPLETE"

	mobility_Graph = clean(mobility_Graph)

	print transportation.nodes_residue, " NODES SKIPPED"

	transportation.draw_roads()
	rd_graph = transportation.get_Roads()
	rd_graph = clean(rd_graph)

	print "Creating rTree for road graph"
	r = getGraphRtree(rd_graph, generator='edges', filename = None, interleaved=True)
	print "Creating rTree complete"

	dict_of_edge_id = {}
	for i, (nodea, nodeb, key) in enumerate(rd_graph.edges(keys=True)) :
		dict_of_edge_id[ str(nodea) + '-' + str(nodeb) + '-' + str(key) ] = i

	print "Linking", len(transportation.to_eulerian) ,"wayless relations"
	for key,value in transportation.to_eulerian.items() :
		if value == {} :
			print "No treatment for", key, "empty dictionnary"
			continue
		else :
			print "LINE IN PROGRESS : ", key
			R = tla.eulerian(rd_graph,value,key,r,dict_of_edge_id,csvfile)
			rd_graph, dict_of_edge_id, r = R[0], R[1], R[2]

	print "Merging the two graphs"
	nds = list( mobility_Graph.nodes )
	edg = list( mobility_Graph.edges(keys=True) )
	liste = []
	for k in range ( len(nds) ):
		liste.append( (nds[k],mobility_Graph.nodes[nds[k]]) )
	rd_graph.add_nodes_from( liste )	
	liste = []
	for k in range ( len(edg) ):
		liste.append( (edg[k][0], edg[k][1],mobility_Graph[ edg[k][0] ][ edg[k][1] ][ edg[k][2] ]) )
	rd_graph.add_edges_from( liste )

	mobility_Graph = rd_graph


	print "Linking Transportation-Roads"
	mobility_Graph = linkToRoads(mobility_Graph,rd_graph,filename,r, dict_of_edge_id, csvfile)

	filer = open('report_dict_ids.csv', 'w')
	for key, value in dict_of_edge_id.items() :
		txt = str(key) + ";" + str(value)
		filer.write(txt.encode('utf-8'))
	filer.close()

	csvfile.close()

	transportation.draw_bounds()
	bounds_Grpah = transportation.get_Bounds()

	if False :
		print "WRITING BOUNDS GRAPH"
		nx.write_gexf(bounds_Grpah, '/home/alex/Bureau/Bounds-lyon-30-8tr.gexf')
		print "FILE COMPLETE"

	print "ADDING BOUNDS", len( mobility_Graph.nodes ), len( mobility_Graph.edges )
	nds = list( bounds_Grpah.nodes )
	edg = list( bounds_Grpah.edges(data=True) )
	liste = []
	print len(nds), len(edg)
	for k in range ( len(nds) ):
		liste.append( (nds[k],bounds_Grpah.nodes[nds[k]]) )
	mobility_Graph.add_nodes_from( liste )	
	liste = []
	for ddd,aaa,datas in edg :
		liste.append( (ddd, aaa, datas ) )
	mobility_Graph.add_edges_from( liste )
	print "BOUNDS ADDED", len( mobility_Graph.nodes ), len( mobility_Graph.edges )

	return mobility_Graph


def city_bounds (filename) :

	Mobility_Graph = nx.MultiDiGraph()

	transportation = Transportation()
	transport_data = je_parse(filename)

	transportation.nodes, transportation.ways, transportation.relations = transport_data[0], transport_data[1], transport_data[2]

	Mobility_Graph = draw_boundaries(Mobility_Graph, transportation.nodes, transportation.ways)



if __name__ == "__main__":

	only = True
	if only :
		os.chdir('/home/alex/Bureau/data-test')

		graphs = cityMobility('/home/alex/Bureau/data-test/lille-total.osm', transportationGraph = True)
		#graphs = cityMobility('/media/alex/9A22-3B35/graphs/marseille-total.osm', transportationGraph = True)

		add_accessibility = True
		if add_accessibility :
			print "ADD ACCESSIBILITY 30 MINUTES"
			dep = 0
			while not dep in list(graphs.nodes) :
				dep = int(input("Saisissez le noeud de départ : "))
			to_add = acc.application(dep, graph = graphs)
			nx.set_node_attributes(graphs,to_add)

		add_isochrone = False
		if add_isochrone :
			dep = int(input("Saisissez le noeud de départ (isochrone) : "))
			graphs = drw.isochrone(dep, graph = graphs)

		print "RESCALING..."
		graphs = rescale_esthetic(graphs)

		print "WRITING FINAL GRAPH"
		nx.write_gexf(graphs, '/home/alex/Bureau/data-test/lille-31-8tr.gexf')

	else :

		L = os.listdir('/media/alex/9A22-3B35/policosm_data')

		for k in range (len(L)) :
			print L[k]

			graphs = cityMobility('/media/alex/9A22-3B35/policosm_data/' + L[k] , transportationGraph = False)
			#graphs = cityMobility('/media/alex/9A22-3B35/graphs/marseille-total.osm', transportationGraph = True)

			add_accessibility = True
			if add_accessibility :
				print "ADD ACCESSIBILITY 30 MINUTES"
				dep = 0
				while not dep in list(graphs.nodes) :
					dep = int(input("Saisissez le noeud de départ : "))
				to_add = acc.application(dep, graph = graphs)
				nx.set_node_attributes(graphs,to_add)

			add_isochrone = False
			if add_isochrone :
				dep = int(input("Saisissez le noeud de départ (isochrone) : "))
				graphs = drw.isochrone(dep, graph = graphs)

			print "RESCALING..."
			graphs = rescale_esthetic(graphs)

			print "WRITING FINAL GRAPH"
			nx.write_gexf(graphs, '/media/alex/9A22-3B35/policosm_results/' + L[k][0:-4] +'.gexf')
