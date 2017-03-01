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

import networkx as nx
import matplotlib.pyplot as plt
import time
from time import localtime, strftime

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from policosm.extractors import roadsGraph, buildingsPolygons
from policosm.classes.distances import Distances, customMetric
from policosm.geoNetworks import clean, addMetricDistanceToEdges, simplify, linkNewNodes, addTimeTraveltoEdges, connectGraphComponents
from policosm.functions import *
from policosm.geoFunctions import getEPSG

begin = localtime()
print strftime("%H:%M:%S", localtime())
filename = '/Volumes/Fabien/Research/cities-pictures/data/France/1-pbf/01249.pbf'
# filename = '/Users/fabien/workspace/github/policosm/policosm/tests/miribel-extract.osm'
graph = roadsGraph(filename)
polygons = buildingsPolygons(filename)

graph = clean(graph)
print strftime("%H:%M:%S", localtime()), 'graph is clean'

sampleNode = graph.nodes(data=True)[0]
sampleLongitude = sampleNode[1]['longitude']
sampleLatitude = sampleNode[1]['latitude']
epsg = getEPSG.epsgFromCoordinates('France', sampleLongitude, sampleLatitude)

buildingsCentroids = getCentroidsFromBuildingsPolygons(polygons)
print strftime("%H:%M:%S", localtime()), 'got building centroids'

graph = linkNewNodes(graph, buildingsCentroids, epsgCode=int(epsg))
print strftime("%H:%M:%S", localtime()), 'finished linking centroids to graph'

print 'graph has',nx.number_connected_components(graph),'component' 
graph = connectGraphComponents(graph, connectNearest=True)
print strftime("%H:%M:%S", localtime()),'finished graph reconnection'

graph  = addMetricDistanceToEdges(graph, int(epsg))
print strftime("%H:%M:%S", localtime()), 'finished graph metric calculation'

graph = simplify(graph)
print strftime("%H:%M:%S", localtime()), 'finished graph simplification'

graph = addTimeTraveltoEdges(graph, ['motorist'])
print strftime("%H:%M:%S", localtime()), 'finished calculating time'

distance = Distances(graph)
distance.allPairs()
# distance.loadPairs('/Users/fabien/workspace/github/policosm/policosm/tests/01249')
print strftime("%H:%M:%S", localtime()), 'finished calculation of all pairs' 

distance.setEPSGDestination(int(epsg))
distance.setWeightForKDE('motorist')
kernel, positions, x, y, bbox, bandwith = getKernelDensityEstimation(buildingsCentroids, metric='pyfunc',metric_params={"func":customMetric, 'object':distance}, optimizeBandwidth=True, bwmin=10, bwmax=500, bandwidth=27.9310344828)
print strftime("%H:%M:%S", localtime()), 'finished kernel calculation ', bbox, bandwith

# title = 'custom metric KDE\nbw: '+str(bandwith)+' motorist'
# plt.title(title, x=0.5, y=0.92, fontsize=12)
# k_pos = np.exp(kernel.score_samples(zip(*positions)))
# print strftime("%H:%M:%S", localtime()), 'finished sampling',len(k_pos)
# kde = np.reshape(k_pos.T, x.shape)
# print strftime("%H:%M:%S", localtime()), 'ready to draw'
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.imshow(np.rot90(kde), cmap=plt.cm.YlOrBr, extent=bbox)
# ax.contour(x, y, kde, 5, colors='k', linewidths=0.6)
# minx, maxx, miny, maxy = bbox
# ax.set_xlim(minx,maxx)
# ax.set_ylim(miny,maxy)
# pictureFilename = filename.split('/')[-1].split('.')[-2]+'png'
# plt.savefig(pictureFilename, dpi=300)




