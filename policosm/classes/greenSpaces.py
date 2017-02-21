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

class GreenSpaces(object):
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
			pass