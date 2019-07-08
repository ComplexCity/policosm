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
sys.path.insert(0, '/Users/fabien/Documents/workspace/github/policosm')

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

'''
http://wiki.openstreetmap.org/wiki/Vegetation

natural=tree		An individual tree, if it is significant.
natural=tree_row	A tree row along rivers or roads
natural=wood		Natural primeval woodland (ie, not managed or harvested).
wood=* leaf_type=* and leaf_cycle=* for additional properties about the woodland.
landuse=forest		Managed forest or woodland plantation
wood=* leaf_type=* and leaf_cycle=* for additional properties about the woodland.
landuse=orchard		Trees or shrubs planted for food production.

Scrub
natural=heath		Uncultivated land with bushes but no tree cover.
natural=scrub		Denser bush coverage than heath.
landuse=vineyard	Vines for grape production.
barrier=hedge		Shrubs arranged in a dense line to form an impassable hedge.

No trees/bushes
natural=wetland		Waterlogged area.
wetland=* 			for additional wetland properties.
natural=marsh		As wetland, but deprecated.
natural=grassland	Natural areas where the vegetation is dominated by grasses (Poaceae) and other herbaceous (non-woody) plants.
landuse=grass		See also surface=grass
landuse=meadow		An area of meadow, which is an area of land primarily vegetated by grass plus other non-woody plants.
natural=fell		Elevated areas naturally free of trees due to climate
landuse=greenfield	An undeveloped area (usually grass) on which construction is planned.
landuse=village_green	An open area of grass in the centre of an English village.
landuse=recreation_ground	An open area of grass used for general recreation.

Other
leisure=garden		Place where flowers and other plants are grown in a decorative and structured manner or for scientific purposes.
leisure=park		Open, green area for recreation, usually municipal.
surface=*

somtimes 
laisure=common

'''