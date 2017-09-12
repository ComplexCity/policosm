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

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

# TODO 

class Transportation(object):
	def __init__(self):
		self.coords = {}
		self.nodes = {}
		self.ways = {}
		self.relations = {}

	def osmcoordinates(self, coords):
		for osmid, lon, lat in coords:
			self.coords[osmid] = (lon, lat)

	def osmnodes(self, nodes):
		for osmid, tags, coords in nodes:
			name = tags['name'] if 'name' in tags else None
			highway = tags['highway'] if 'highway' in tags else None
			bus = tags['bus'] if 'bus' in tags else None
			public_transport = tags['public_transport'] if 'public_transport' in tags else None
			network = tags['network'] if 'network' in tags else None 
			operator = tags['operator'] if 'operator' in tags else None
			self.nodes[osmid]=(coords, name, highway, bus, public_transport, network, operator)

	def osmways(self, ways):
		for osmid, tags, refs in ways:
			#tag 
			self.ways[osmid] = (refs, tags)

	def osmrelations(self, relations):
		for osmid, tags, members in relations:
			# tag name network operator ref route_master type (route_master) wheelchair
			# tag name network operator ref route type (route) wheelchair
			if 'route' in tags['type']:
				self.relations[osmid] = (tags, members)

	def info(self):
		info =  'nodes:' + str(len(self.nodes)) + '\n'
		info += 'ways:' + str(len(self.ways)) + '\n'
		info += 'relations:' + str(len(self.relations)) + '\n'
		return info

class Bus(Transportation):
	def __init__(self, coords={}, nodes={}, ways={}, relations={}):
		if nodes is None and ways is None and relations is None:
			super(Transportation, self).__init__()
		else:
			self.coords = coords
			self.nodes = nodes
			self.ways = ways
			self.relations = relations

	def analyseBus(self):
		print self.nodes.keys()
		relations = {}
		for keyOsmid, (tags, members) in self.relations.iteritems():
			if 'route' in tags:
				if tags['route'] <> 'bus':
					continue
			if 'route_master' in tags:
				if tags['route_master'] <> 'bus':
					continue
			#prepare ways
			relations[keyOsmid] = (tags, members)
			print tags
			for osmid, osmType, osmDetail in members:
				if osmType == 'node':
					try:
						if osmid in self.nodes:
							print 'NODE',self.nodes[osmid], osmDetail
						else:
							print 'NODE ######',self.coords[osmid],osmDetail
					except Exception, e:
						print 'NODE out of town'
				elif osmType == 'way':
					try:
						print 'WAY', self.ways[osmid], osmDetail
					except Exception, e:
						print 'WAY out of town'

			# TODO RECREATE THE GRAPH WITH A GRAPH FOR EACH LINE ADDING STOPS
					
			self.relations = relations

			#prepare nodes
			# TODO IF DISTANCE IS TOO SHORT, MUST BE TWO SIDES OF THE ROAD ! Keep points ?
			# NODE ON THE RIGHT OF THE WAY ONE DIRECTION
			# NODE ON THE OTHER SIDE ANOTHER DIRECTION


'''
one master relation with some properties

-> some relations for each way

each relations has nodes and ways 

stops can be node or polygon

'''

if __name__ == "__main__":
	from imposm.parser import OSMParser
	transportation = Transportation()
	osmParser = OSMParser(concurrency=4, coords_callback=transportation.osmcoordinates, nodes_callback=transportation.osmnodes, ways_callback=transportation.osmways, relations_callback=transportation.osmrelations)
	osmParser.parse('/Users/fabien/workspace/github/policosm/policosm/tests/01249.pbf')
	print transportation.info()
	bus = Bus(coords=transportation.coords, nodes=transportation.nodes, ways=transportation.ways, relations=transportation.relations)
	bus.analyseBus()
	print bus.info()

