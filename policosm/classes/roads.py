#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	Roads sets callback functions for ways in osm files targeting roads

parameters

how it works

return

'''

import networkx as nx
import re

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from policosm.utils.roads import levels

class Roads(object):

	graph = nx.Graph()
	verbose = False

	def __init__(self, verbose=False):
		self.verbose = verbose

	def getGraph(self):
		return self.graph

	def nodes(self, coords):
		for osmid, lon, lat in coords:
			self.graph.add_node(osmid,longitude=float(lon), latitude=float(lat))

	def edges(self, ways):
		for osmid, tags, refs in ways:
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
				if 'foot' in tags:
					footway = True if tags['foot'] == 'yes' else False 
				elif highway == 'pedestrian' or highway == 'footway':
					footway = True
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
						if self.verbose:
							print 'lanes tag value error for',tags['lanes'],'for osmid',osmid,'default to 1'
				
				# update HIGHWAY information from the tag 'highway'
				# if highway tag is not osm compliant, highway is defaulted to 'unclassified'
				try:
					highway.encode('ascii')
				except UnicodeEncodeError:
					highway = 'unclassified'

				for levelItem in levels['levels']:
					key, values = levelItem.keys()[0], levelItem.values()[0]
					if str(highway).lower() in values:
						level = key
				
				# if the level is unknow you might want to include it in the level file (roadTypes.py)
				# it oftens comes from miswritten osm tag
				if level == -1:
					if self.verbose:
						print 'highway tag',highway,'unknow for osmid',osmid,'default to level 3'
					level = 3

				for i in range(1, len(refs)):
					self.graph.add_edge(refs[i-1], refs[i], osmid=osmid, highway=str(highway), level=int(level), lanes=lanes, oneway=oneway)

if __name__ == "__main__":
	testGraph = nx.Graph()
	testGraph.add_node(1,longitude=1.0, latitude=1.0)
	testGraph.add_node(2,longitude=2.0, latitude=2.0)
	testGraph.add_edge(1, 2,osmid=3,highway='residential',level=3, lanes=1, oneway=False)

	roads = Roads()
	roads.nodes([[1,1.0,1.0],[2,2.0,2.0]])
	roads.edges([[3,{'highway':'residential', 'lanes':'yes'},[1,2]]])
	
	# test nodes
	nl1 = list(testGraph.nodes(data=True))
	nl2 = list(roads.graph.nodes(data=True))
	d1 = dict(nl1)
	d2 = dict(nl2)
	assert d1 == d2

	# test edges
	from collections import defaultdict
	d1 = defaultdict(dict)
	d2 = defaultdict(dict)
	c1 = 0
	for c1,e in enumerate(testGraph.edges(data=True)):
		u,v = e[0],e[1]
		data = e[2:]
		d1[u][v] = data
		d1[v][u] = data
		c2 = 0
	for c2,e in enumerate(roads.graph.edges(data=True)):
		u,v = e[0],e[1]
		data = e[2:]
		d2[u][v] = data
		d2[v][u] = data
	assert c1 == c2
	assert d1 == d2




