#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende
'''

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

import geojson
from shapely.geometry import Polygon, LineString, asShape, mapping

class Within(object):
    def __init__(self, o):
        self.o = o
    def __lt__(self, other):
        return self.o.within(other.o)


class Test_Buildings_class(object):
	def test_nodes(self, coords):
		for osmid, lon, lat in coords:
			self.coordinates[osmid]=(lon, lat)

	def test_osmways(self, ways):
		for osmid, tags, refs in ways:
			
			building = False
			if 'building' in tags:
				building = True
			
			amenity = tags['amenity'] if 'amenity' in tags else 'unknown'
			
			wheelchair = False
			if 'wheelchair' in tags:
				wheelchair = True if tags['wheelchair'] == 'yes' else False
			
			buildingLevels = -1
			if 'building:levels' in tags:
				buildingLevels = int(tags['building:levels'])

			self.ways[osmid] = (refs,building,amenity,wheelchair,buildingLevels)

	def test_osmrelations(self, relations):
		for osmid, tags, members in relations:
			if 'type' in tags:
				if tags['type'] == 'multipolygon':
					self.relations[osmid] = members

	def test_getPolygons(self, keepUncompletePolygons=True):
		features = []

		# for polygons in relations (especially outer/innner) 
		# online forums suggest to not trust the outer tag
		# so we rather test it by ourselves
		for k, members in self.relations.iteritems():
			polygons = []
			properties = {}
			for osmid,relType,role in members:
				# if the way does not belong to a building
				if osmid not in self.ways:
					continue
				elif not self.ways[osmid][1]:
					continue
				polygon = Polygon([self.coordinates[ref] for ref in self.ways[osmid][0]])
				polygons.append(polygon)
			
			if len(polygons) < 2:
				continue

			# sort polygons in whithinness order
			# if they are all inside the first we make a polygon with holes
			polygons = sorted(polygons, key=Within, reverse=True)	
			if Within(polygons[1]) < Within(polygons[0]):
				polygon = geojson.Polygon([list(mapping(p)['coordinates'][0]) for p in polygons])
				refs,building,amenity,wheelchair,buildingLevels = self.ways[members[0][0]]
				properties = {'osmid':k,'amenity':amenity,'wheelchair':wheelchair,'levels':buildingLevels}
				features.append(geojson.Feature(geometry=polygon, properties=properties))
				
				for osmid,relType,role in members:
					del self.ways[osmid]
		
		for osmid, (refs,building,amenity,wheelchair,buildingLevels) in self.ways.iteritems():
			if building:
				polygon = [[tuple(self.coordinates[ref]) for ref in refs if ref in self.coordinates]] 
				if keepUncompletePolygons:
					if len(polygon[0]) < 3: 
						continue
				elif len(polygon[0]) != len(refs):
					continue
				properties = {'osmid':osmid,'amenity':amenity,'wheelchair':wheelchair,'levels':buildingLevels}
				features.append(geojson.Feature(geometry=geojson.Polygon(polygon), properties=properties))
		featureCollection = geojson.FeatureCollection(features)
		return featureCollection

if __name__ == "__main__":
	from imposm.parser import OSMParser
	buildings = Buildings()
	osmparser = OSMParser(concurrency=4, coords_callback=buildings.nodes, ways_callback=buildings.osmways, relations_callback=buildings.osmrelations)
	osmparser.parse('/Users/fabien/workspace/cities-pictures/data/France/1-pbf/lille.osm.pbf')
	# print geojson.dumps(buildings.getPolygons())
	print '[info] there is',len(buildings.getPolygons()['features'])
