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
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from policosm.extractors import roadsGraph, buildingsPolygons
from policosm.geoNetworks import clean, simplify
from policosm.functions import getCentroidsFromRoadsGraph, getCentroidsFromBuildingsPolygons, getBoundaries, getKernelDensityEstimation
from policosm.utils.cities import getCitiesPBF

filename = '/Volumes/Fabien/Research/cities-pictures/data/France/1-pbf/' + getCitiesPBF('Miribel')
graph = roadsGraph(filename)
graph = clean(graph)
graph = simplify(graph)
roadsCentroids = getCentroidsFromRoadsGraph(graph)
print 'starting kde for centroids:',len(roadsCentroids)
bbox = getBoundaries.getRoadsBoundaries(graph)
kernel1, positions1, x1, y1, bbox1, bandwith1 = getKernelDensityEstimation(roadsCentroids, metric='euclidean', bbox=bbox, bandwidth=0.001124, optimizeBandwidth=True)

polygons = buildingsPolygons(filename)
buildingsCentroids = getCentroidsFromBuildingsPolygons(polygons)
print 'starting kde for centroids:',len(buildingsCentroids)
kernel2, positions2, x2, y2, bbox2, bandwith2 = getKernelDensityEstimation(buildingsCentroids, metric='euclidean', bbox=bbox, bandwidth=0.001124, optimizeBandwidth=True)

centroids = roadsCentroids + buildingsCentroids
print 'starting kde for centroids:',len(centroids)
kernel3, positions3, x3, y3, bbox3, bandwith3 = getKernelDensityEstimation(centroids, bbox=bbox, metric='euclidean', bandwidth=0.001124, optimizeBandwidth=True)

# # Plot

# kernel2, positions2, x2, y2, bbox2, bandwith2 = kernel1, positions1, x1, y1, bbox1, bandwith1
# kernel3, positions3, x3, y3, bbox3, bandwith3 = kernel1, positions1, x1, y1, bbox1, bandwith1

fig = plt.figure(figsize=(40, 10))
gs = gridspec.GridSpec(1, 3)

plt.subplot(gs[0])
title = 'Roads KDE\nbw: '+str(bandwith1)+' euclidean'
plt.title(title, x=0.5, y=0.92, fontsize=12)
k_pos1 = np.exp(kernel1.score_samples(zip(*positions1)))
kde1 = np.reshape(k_pos1.T, x1.shape)
plt.imshow(np.rot90(kde1), cmap=plt.cm.YlOrBr, extent=bbox)
plt.contour(x1, y1, kde1, 5, colors='k', linewidths=0.6)

plt.subplot(gs[1])
title = 'Buildings KDE\nbw: '+str(bandwith2)+' euclidean'
plt.title(title, x=0.5, y=0.92, fontsize=12)
k_pos2 = np.exp(kernel2.score_samples(zip(*positions2)))
kde2 = np.reshape(k_pos2.T, x2.shape)
plt.imshow(np.rot90(kde2), cmap=plt.cm.YlOrBr, extent=bbox)
plt.contour(x2, y2, kde2, 5, colors='k', linewidths=0.6)

plt.subplot(gs[2])
title = 'Roads + Buildings KDE\nbw: '+str(bandwith3)+' euclidean'
plt.title(title, x=0.5, y=0.92, fontsize=12)
k_pos3 = np.exp(kernel3.score_samples(zip(*positions3)))
kde3 = np.reshape(k_pos3.T, x3.shape)
plt.imshow(np.rot90(kde3), cmap=plt.cm.YlOrBr, extent=bbox)
plt.contour(x3, y3, kde3, 5, colors='k', linewidths=0.6)

fig.tight_layout()
plt.show()