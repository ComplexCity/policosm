#!/usr/bin/python
# -*- coding: utf-8 -*-

# Complexcity project | Author : Thomas Erussard
# functions from Fabien Pfaender
# example : Saint Malo 35

# import >

from osgeo import gdal, ogr, osr
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import csv

# find east west north south extreme >

def getRoadsBoundaries(graph):
    lons = nx.get_node_attributes(graph, 'longitude').values()  # tableau long
    lats = nx.get_node_attributes(graph, 'latitude').values()

    bounds = [min(lons), min(lats), max(lons), max(lats)]
    return bounds


# switch to epsg (meters) 4326 3948 >

def convertNodesCoordinates(graph, sourceEPSG, targetEPSG):
    sourceProjection = osr.SpatialReference()
    sourceProjection.ImportFromEPSG(sourceEPSG)
    destinationProjection = osr.SpatialReference()
    destinationProjection.ImportFromEPSG(targetEPSG)
    coordTrans = osr.CoordinateTransformation(sourceProjection, destinationProjection)
    for node in graph.nodes():
        x, y = graph.node[node]['longitude'], graph.node[node]['latitude']
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)
        point.Transform(coordTrans)
        graph.node[node]['longitude'], graph.node[node]['latitude'] = point.GetX(), point.GetY()
    return graph

# include my geotiff >


def getValue((layer, gt), x, y):
    rasterx = int((x - gt[0]) / gt[1])
    rastery = int((y - gt[3]) / gt[5])

    return layer.GetRasterBand(1).ReadAsArray(rasterx, rastery, 1, 1)[0][0]


def getGeotiff():
    root = '/home/ccbaxter/Bureau/Complexcity/Geotiff/'

    file = root + 'SVDNB_npp_20150101-20151231_75N060W_vcm-orm_v10_c201701311200.avg_rade9.tif'

    layer = gdal.Open(file)
    gt = layer.GetGeoTransform()
    return (layer, gt)

# create grid with list of coordinates

def lightValue(f): # get light intensity from coordinate CSVfile
    k = open(f,'rb')
    fileCSV = csv.reader(k)
    rows = []

    for lines in fileCSV:
        x = float(lines[0])
        y = float(lines[1])
        print x, y
        z = getValue((layer, gt), x, y)
        print x,y
        rows.append([x,y,z])

    # mat = np.array(rows)
    with open("/home/ccbaxter/Bureau/Complexcity/CSV/light_pollution_Vernon500.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            writer.writerow(row)

    # np.savetxt("/home/ccbaxter/Bureau/Complexcity/CSV/test100.csv", mat, delimiter=',')


# create windows >

def createWindows(x_min, x_max, y_min, y_max, pas=0.001): # create the visualization (grid and matched values)
    rows = []

    i = x_min
    while i <= x_max:
        j = y_min
        while j <= y_max:
            z = getValue((layer, gt), i, j)
            rows.append([i,j,z])
            j = j + pas
        i = i + pas

    x = np.arange(x_min, x_max, pas)
    y = np.arange(y_min, y_max, pas)

    mat = np.array(rows)

    X, Y = np.meshgrid(x, y)
    Z = griddata((mat[:, 0], mat[:, 1]), mat[:, 2], (X, Y), method='nearest')
    plt.pcolormesh(X, Y, Z)

    # add colorbar.
    plt.colorbar()
    # add title
    plt.title('Light pollution in INSEE number : 64445')
    # add legends

    plt.show()



# test function

if __name__ == "__main__":

    gdal.UseExceptions()
    (layer, gt) = getGeotiff()

    # point test

    # xc = -1.961
    # yc = 48.62
    # print getValue((layer, gt), xc, yc)
    # xc = -1.963
    # yc = 48.62
    # print getValue((layer, gt), xc, yc)

    testGraph = nx.read_gexf('/home/ccbaxter/Bureau/Complexcity/Graph/64445.gexf', node_type=None, relabel=False,
                              version='1.1draft')

    # N°INSEE 64445 : Pau ; 35288 : saint malo ; 27213 : Ecos ; 27681 : vernon

    print nx.info(testGraph) #number of nodes / edges
    bounds = getRoadsBoundaries(testGraph)
    print (bounds) # print geographic limits

    createWindows(bounds[0], bounds[2], bounds[1], bounds[3], 0.001)
    # lightValue('/home/ccbaxter/Bureau/Complexcity/CSV/Vernon/gridVernon500.csv')