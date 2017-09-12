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

class Transportations(object):

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
# bus
#  one relation per direction (also called variant) of a service route, tagged with type=route+route=bus/route=trolleybus.

# Train
# Tag	Description
# Funicular	railway=funicular - Cable driven inclined railways.
# Miniature	railway=miniature - Smaller trains, normally operated as a tourism=attraction
# Monorail	railway=monorail - A railway with only a single rail, often inner city and above street level. Also used for monorail-like automated people-mover systems like Miami's Metromover.
# Narrow-gauge	railway=narrow_gauge - Narrow-gauge passenger or freight trains, often tourist/scenic routes. In some regions narrow gauge railways are used for full sized passenger or freight trains service. See the Rhätische Bahn (RhB) and Matterhorn Gotthard Bahn (MGB) in Switzerland as examples for such full featered narrow gauge railways. Use gauge=* to specify how small narrow is for this railway.
# Preserved	railway=preserved - A railway running historic trains, usually a tourist attraction.
# Mainline	railway=rail - Full sized passenger or freight trains in the standard gauge for the country or state.
# Subway	railway=subway - A city passenger rail service running mostly grade separated (see Wikipedia:rapid transit).
# Tram	railway=tram - City based rail systems with one/two carriage vehicles, often share roads with cars.
# Light rail	railway=light_rail - A higher-standard tram system, normally in its own right-of-way.


# Métros
# railway=subway
# Station
# For subway stations just add one node Node at an appropriate point on the railway track
# railway=station (mandatory)
# station=subway (mandatory)
# name=*
# wheelchair=*
# Routes
# route=subway

# Tram
# Tram tracks are tagged with railway=tram.
# tags public_transport=stop_position and tram=yes. Historically they were mapped with just railway=tram_stop,

# aerial way 
# aerialway	cable_car	Way	[W] Cablecar or Tramway. Just one or two large cars. The traction cable forms a loop, but the cars do not loop around, they just move up and down on their own side, rolling along static cables over which they are suspended.	
# Aerialway gondola render.png
# CH Furtschellas aerial tram.jpg
# gondola	Way	[W] Gondola lift. Many cars on a looped cable.	
# Aerialway gondola render.png
# Linbana kolmården cable car.jpg
# chair_lift	Way	[W] Chairlift. Looped cable with a series of single chairs (typically seating two or four people, but can be more). Exposed to the open air (can have a bubble).
# This implies oneway=yes (drawn upward). Any two-way chairlifts should be tagged oneway=no.	
# Chair lift rendering.png
# Silver Queen Chair, CBMR.jpg
# mixed_lift	Way	[W] Mixed lift Also known as a hybrid lift is a new type of ski lift that combines the elements of a chairlift and a gondola lift.		
# Cgd panoramabahn.jpg
# drag_lift	Way	[W] Drag lift or Surface lift is an overhead tow-line for skiers and riders. A T-bar lift, button lift, or more simple looped rope drag lifts, or loops of wire with handles to grab. See also aerialway=t-bar, aerialway=j-bar, aerialway=platter and aerialway=rope_tow.
# This automatically implies oneway=yes (drawn upward).	
# Chair lift rendering.png
# T-bar lift.JPG
# t-bar	Way	[W] T-bar lift. A type of aerialway=drag_lift.
# This automatically implies oneway=yes (drawn upward).	
# Chair lift rendering.png
# Orczyk.jpg
# j-bar	Way	[W] J-bar lift. A type of aerialway=drag_lift. Like t-bar but just on one side.
# This automatically implies oneway=yes (drawn upward).	
# Chair lift rendering.png
# Coldspgs j bar lift.jpg
# platter	Way	[W] Platter lift. A type of aerialway=drag_lift. Similar to a t-bar, but with a disc instead of a bar. Single-person only.
# This automatically implies oneway=yes (drawn upward).	
# Chair lift rendering.png
# Tellerliftbügel.jpg
# rope_tow	Way	[W] Rope tow. A type of aerialway=drag_lift.
# This automatically implies oneway=yes (drawn upward).	
# Chair lift rendering.png
# Rope tow overview.jpeg
# magic_carpet	Way	[W] Magic carpet. A type of ski lift.
# This automatically implies oneway=yes (drawn upward).		
# Magic carpet uphill loaded P1437.jpeg
# zip_line	Way	[W] Zip line. Simple aerial rope slides.
# This automatically implies oneway=yes (drawn downward).

# Ferries
# route=ferry
# amenity=ferry_terminal

