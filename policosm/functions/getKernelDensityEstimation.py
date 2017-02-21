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
from sklearn.neighbors import KernelDensity
from sklearn.grid_search import GridSearchCV

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

# from policosm.classes.distances import Distances, customMetric

def getKernelDensityEstimation(nodes, metric='euclidean', metric_params=None, bbox=None, bandwidth=0.002, optimizeBandwidth=False, bwmin=0.0001, bwmax=0.01, crossValidation=20):
	lon = []
	lat = []
	for nlon,nlat in nodes:
		lon.append(nlon)
		lat.append(nlat)
	lon = np.array(lon)
	lat = np.array(lat)

	if bbox is None:
		xmin, xmax = min(lon), max(lon)
		ymin, ymax = min(lat), max(lat)
		bbox = [xmin, xmax, ymin, ymax]
	else:
		xmin, ymin, xmax, ymax = bbox[0],bbox[1],bbox[2],bbox[3]
		bbox = [xmin, xmax, ymin, ymax]

	x, y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
	positions = np.vstack([x.ravel(), y.ravel()])
	values = np.vstack([lon, lat])

	if optimizeBandwidth:
		grid = GridSearchCV(KernelDensity(kernel='gaussian', metric=metric, metric_params=metric_params, algorithm='ball_tree'), {'bandwidth': np.linspace(bwmin, bwmax, 30)}, cv=crossValidation) # 20-fold cross-validation
		grid.fit(zip(*values))

		bandwidth = grid.best_params_['bandwidth']
		kernel = grid.best_estimator_
	else:
		kernel = KernelDensity(kernel='gaussian', metric=metric, metric_params=metric_params, algorithm='ball_tree', bandwidth=bandwidth)
		kernel.fit(zip(*values))
	
	return kernel, positions, x, y, bbox, bandwidth

if __name__ == "__main__":
	centroids = [(1.0,1.2),(1.2,1.0),(1.5,1.4),(1.7,1.9),(2.0,1.3),(1.6,1.9)]

	# distance = Distances(None)
	# # kernel, positions, x, y, bbox, bandwith = getKernelDensityEstimation(centroids, metric='euclidean', optimizeBandwidth=True, bwmin=0.1, bwmax=1, crossValidation=6)
	# kernel, positions, x, y, bbox, bandwith = getKernelDensityEstimation(centroids, metric='pyfunc',metric_params={"func":customMetric, 'object':distance}, optimizeBandwidth=False, bwmin=0.1, bwmax=1, crossValidation=6)

	# print 'best estimation for bandwidth',bandwith
	# print  'value for 1.5, 1.5', np.exp(kernel.score_samples([[1.5, 1.5]]))[0]













