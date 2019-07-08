#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	Roads sets callback functions for ways in osm files targeting roads
	the osm roads are transform into graphs

parameters
	functions are called with callback from imposm.parser
	nodes coordinates parameters are in the following format [[id,lon,lat],[id,lon,lat]]
	edges ways 

how it works
	create a series of nodes each time osm parser send nodes
	test a series of rules to create edges each time osm parser send a way
	the node contains latitude and longitude information
	the edge contains ['lanes', 'osmid', 'footway', 'level', 'bicycle', 'oneway', 'highway'] informations

#TODO ADD MAX SPEED TO ROADS

'''

import networkx as nx
import re
import osmium

from policosm.utils.roads import levels

class Roads(osmium.SimpleHandler):
	def __init__(self, verbose=False):
		osmium.SimpleHandler.__init__(self)
		self.verbose = verbose
		self.graph = nx.Graph()


	def getGraph(self):
		return self.graph

	def node(self, n):
		osmid = n.id
		lon = n.location.lon
		lat = n.location.lat
		self.graph.add_node(osmid,longitude=lon, latitude=lat)

	def way(self, w):
		#for osmid, tags, refs in ways:
		osmid = w.id
		tags = w.tags
		print(tags,osmid)
		if 'highway' in tags:
			highway = tags['highway']
			bicycle = False
			footway = True
			oneway = False
			lanes = 1
			level = -1
			
			# Update BICYCLING information using specific tag (priority) or 'highway' tag
			if 'bicycle' in tags:
				bicycle = True if tags['bicycle'] == 'yes' or tags['bicycle'] == 'designated' else False
			elif highway == 'cycleway' or highway == 'cyleway' :
				bicycle = True
			else:
				bicycle = False

			# Update PEDESTRIAN information using specific tag (priority) or 'highway' tag
			if 'foot' in w.tags:
				footway = True if tags['foot'] == 'yes' else False 
			elif highway == 'pedestrian' or highway == 'footway':
				footway = True
			else:
				footway = False

			if 'oneway' in w.tags:
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
				except ValueError:
					lanes = 1
					if self.verbose:
						print ('lanes tag value error for',tags['lanes'],'for osmid',osmid,'default to 1')
				
			#TODO add sidewalk information

			# update HIGHWAY information from the tag 'highway'
			# if highway tag is not osm compliant, highway is defaulted to 'unclassified'
			try:
				highway.encode('ascii')
			except UnicodeDecodeError:
				highway = 'unclassified'

			for l in levels['levels']:
				if str(highway).lower() in l.values():
					level = l.keys()[0]
					break
			
			# if the level is unknow you might want to include it in the level file (roadTypes.py)
			# it oftens comes from miswritten osm tag
			if level == -1:
				if self.verbose:
					print ('highway tag',highway,'unknow for osmid',osmid,'default to level 3')
				level = 3
			print('nodes founds in the way are',w.nodes,len(w.nodes))
			for i in range(1, len(w.nodes)):
				self.graph.add_edge(w.nodes[i-1].ref, w.nodes[i].ref, osmid=osmid, highway=str(highway), level=int(level), lanes=lanes, oneway=oneway, footway=footway, bicycle=bicycle)

