#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
extract a graph from 

parameters
graph

how it works

return


'''

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

import geojson
from shapely.geometry import shape

def getAreaWeightedCentroidsFromBuildingsPolygons(polygons):
	centroids = []
	for feature in polygons['features']:
		polygon = shape(feature['geometry'])
		x = polygon.centroid.x
		y = polygon.centroid.y
		area = polygon.area
		centroids.append((x, y, area))
	return centroids

def getCentroidsFromBuildingsPolygons(polygons):
	centroids = []
	for feature in polygons['features']:
		polygon = shape(feature['geometry'])
		x = polygon.centroid.x
		y = polygon.centroid.y
		centroids.append((x, y))
	return centroids

def getAreaWeightedCentroidFromBuildingsPolygons(polygons, normalized=False):
	x=0.0
	y=0.0
	area = 0
	centroids = getAreaWeightedCentroidsFromBuildingsPolygons(polygons)
	for xc, yc, areac in centroids:
		x += xc
		y += yc
		area+=areac
	if normalized:
		return (x/len(centroids),y/len(centroids),area/len(centroids))
	else:
		return (x/len(centroids),y/len(centroids),area)


def getCentroidFromBuildingsPolygons(polygons):
	x=0.0
	y=0.0
	centroids = getCentroidsFromBuildingsPolygons(polygons)
	for xc, yc in centroids:
		x += xc
		y += yc
	return (x/len(centroids),y/len(centroids))

if __name__ == "__main__":
	polygons = geojson.loads('{ "type": "FeatureCollection","features": [{ "type": "Feature","geometry": {"type": "Polygon", "coordinates": [[ [0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0] ] ] }, "properties": {"prop0": "value0", "prop1": {"this": "that"} } } ] }')
	assert getCentroidsFromBuildingsPolygons(polygons) == [(5.0, 5.0)] 
	print(getCentroidsFromBuildingsPolygons(polygons))
	print(getCentroidFromBuildingsPolygons(polygons))



