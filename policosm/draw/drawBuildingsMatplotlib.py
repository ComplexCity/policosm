#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
clean roads graph created from osm file

parameters
graph

how it works
1 - remove nodes without geographic informations (latitude or longitude)
2 - remove self referencing edges (loop on itself)
3 - remove isolated nodes (degree is 0 )

return
graph minus alone or non-conform nodes

'''
import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

import matplotlib.pyplot as plt
from descartes.patch import PolygonPatch
import colorlover as cl
from shapely.geometry import Polygon, shape
import random


from policosm.extractors.buildingsPolygons import *
import policosm.geoNetworks as pocogeo
from policosm.functions import *

def drawBuildings(polygons, displayRatio=1.0):
	fig = plt.figure()
	ax = fig.add_subplot(111)	
	for feature in polygons['features']:
		if displayRatio < 1.0:
			if random.random() >= displayRatio:
				continue
		polygon = shape(feature['geometry'])
		patch = PolygonPatch(polygon, facecolor='#FD7400', edgecolor='#FD7400', alpha=0.5, zorder=1)
		ax.add_patch(patch)
	
	bounds = getBuildingsBoundaries(polygons)
	minx, miny, maxx, maxy = bounds
	ax.set_xlim(minx,maxx)
	ax.set_ylim(miny,maxy)

	plt.show()

if __name__ == "__main__":
	filename = '/Volumes/Fabien/Research/cities-pictures/data/France/1-pbf/74173.pbf'
	polygons = buildingsPolygons(filename)
	drawBuildings(polygons)