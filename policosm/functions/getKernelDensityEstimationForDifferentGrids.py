# coding=utf-8
import numpy as np
from sklearn.neighbors import KernelDensity
from sklearn.grid_search import GridSearchCV


#  parameter grid_sizes represents all the different grids we want to compute
# it is a list of length between points for each grid, default value is 100
def getKernelDensityEstimationForDifferentGrids(nodes, metric='euclidean', metric_params=None, bandwidth=0.002,
                                                optimizeBandwidth=False, bwmin=0.0001, bwmax=0.01, crossValidation=20,
                                                grid_sizes=None):
    lon = []
    lat = []
    for nlon, nlat in nodes:
        lon.append(nlon)
        lat.append(nlat)
    lon = np.array(lon)
    lat = np.array(lat)

    # bbox automatically calculated
    xmin, xmax = min(lon), max(lon)
    ymin, ymax = min(lat), max(lat)
    bbox = [xmin, xmax, ymin, ymax]

    # grid size every 100m, 250m, 500m
    # list of x and y for each grid sizes
    # xy = [np.mgrid[xmin:xmax:i, ymin:ymax:i] for i in [100, 250, 500]]
    xy = [np.mgrid[xmin:xmax:i, ymin:ymax:i]
          if grid_sizes is not None
          else np.mgrid[xmin:xmax:100, ymin:ymax:100]
          for i in grid_sizes]
    # list of grids
    positions = [np.vstack([x.ravel(), y.ravel()]) for x, y in xy]

    # build single D matrix for grid (positions) and data (values)
    values = np.vstack([lon, lat])

    if optimizeBandwidth:
        grid = GridSearchCV(
            KernelDensity(kernel='gaussian', metric=metric, metric_params=metric_params, algorithm='ball_tree'),
            {'bandwidth': np.linspace(bwmin, bwmax, 30)}, cv=crossValidation)  # 20-fold cross-validation
        grid.fit(zip(*values))

        bandwidth = grid.best_params_['bandwidth']
        kernel = grid.best_estimator_
    else:
        kernel = KernelDensity(kernel='gaussian', metric=metric, metric_params=metric_params, algorithm='ball_tree',
                               bandwidth=bandwidth)
        kernel.fit(zip(*values))

    return kernel, positions, xy, bbox, bandwidth
