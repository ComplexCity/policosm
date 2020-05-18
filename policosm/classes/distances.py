#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does

parameters

how it works

return

'''

import pickle
import sys

import networkx as nx
from shapely.geometry import Point, LineString

sys.path.insert(0, '/Users/fabien/Documents/workspace/github/policosm')

from policosm.functions.getRtree import getGraphRtree
from policosm.geoNetworks.linkNewNodes import nearestEdgeFromPoint
from policosm.utils.levels import France

class Distances(object):


	def __init__(self, graph, weight=None, verbose=False):
		self.verbose = verbose
		self.graph = graph
		self.allowPublicTransportation = None
		self.pedestrian = None
		self.motorist = None
		self.publicTransportion = None
		self.r = None
		self.weight = weight
		self.epsgDestination = None

	def setWeightForKDE(self, weight):
		self.weight = weight

	def setRtree(self, r):
		self.r = r

	def setEPSGDestination(self,destination):
		self.epsgDestination = destination

	def savePairs(self, filename, weight='motorist'):
		with open(filename + '-' + weight + '.pkl', 'wb+') as ofp:
			if weight == 'motorist':
				pickle.dump(self.motorist, ofp)
			elif weight == 'pedestrian':
				pickle.load(self.pedestrian, ofp)
			elif weight == 'publicTransportion':
				pickle.load(self.publicTransportion, ofp)
			else:
				raise 'unknown weight'
	
	def loadPairs(self, filename, weight='motorist'):
		with open(filename + '-' + weight + '.pkl', 'rb') as ifp:
			if weight == 'motorist':
				self.motorist = pickle.load(ifp)
			elif weight == 'pedestrian':
				self.pedestrian = pickle.load(ifp)
			elif weight == 'publicTransportion':
				self.publicTransportion = pickle.load(ifp)
			else:
				raise 'unknown weight'

	def allPairs(self, weight='motorist'):
		if weight == 'motorist':
			self.motorist = nx.all_pairs_dijkstra_path_length(self.graph, weight=weight)
		elif weight == 'pedestrian':
			self.pedestrian = nx.all_pairs_dijkstra_path_length(self.graph, weight=weight)
		elif weight == 'publicTransportion':
			self.publicTransportion = nx.all_pairs_dijkstra_path_length(self.graph, weight=weight)
		else:
			raise 'unknown weight'

	def graphRtree(self,rtreeFilename=None):
		self.r = getGraphRtree(self.graph,generator='edges',filename=rtreeFilename,interleaved=True)

	def closestNodeOnTheGraph(self, x, y):
		if self.r is None:
			self.graphRtree()

		z = Point(x,y)

		hits = self.r.nearest((x, y, x, y), 2, objects="raw")
		u,v =  nearestEdgeFromPoint(list(hits), Point(x,y))

		ucoo = (self.graph.node[u]['longitude'], self.graph.node[u]['latitude'])
		vcoo = (self.graph.node[v]['longitude'], self.graph.node[v]['latitude'])
		
		line = LineString([ucoo,vcoo])
		lineLength = line.length
		segmentLength = line.project(z)

		if self.weight == 'motorist':
			speed = France['speeds'][2]

		if segmentLength < lineLength/2:
			w = Point(ucoo[0],ucoo[1])
			if self.epsgDestination is not None:
				distance = addMetricDistanceToEdge(w.x, w.y, z.x, z.y, self.epsgDestination) / (speed * 1000 / 3600.0)
			else:
				distance = w.distance(z) / (speed * 1000 / 3600.0)
			return u, distance

		elif segmentLength > lineLength/2:
			w = Point(vcoo[0],vcoo[1])
			if self.epsgDestination is not None:
				distance = addMetricDistanceToEdge(w.x, w.y, z.x, z.y, self.epsgDestination) / (speed * 1000 / 3600.0)
			else:
				distance = w.distance(z) / (speed * 1000 / 3600.0)
			return v, distance
	
	def pairwise(self, x, y):
		x1, y1 = x[0], x[1]
		x2, y2 = y[0], y[1]
		n1, d1 = self.closestNodeOnTheGraph(x1, y1)
		n2, d2 = self.closestNodeOnTheGraph(x2, y2)

		value =  None

		if self.weight == 'motorist':
			try:
				value = self.motorist[n1][n2]
			except KeyError as e:
				# if no node link the two we find the two closest on the the two networks
				raise e
		return value + d1 + d2


def customMetric(x, y, **kwargs):
	distance = kwargs['object']
	# print 'x', x
	# print 'y', y
	if len(x) > 2:
		return 0
	else:
		return distance.pairwise(x,y)
