#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in July 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	
parameters
	
how it works
	
return
	
'''

import networkx as nx
from osgeo import ogr, osr

from policosm.utils.projections import get_most_accurate_epsg


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


if __name__ == "__main__":
    testGraph = nx.Graph()
    x, y = (4.9528934, 45.8224652)
    testGraph.add_node(1, longitude=x, latitude=y)
    print(testGraph.node[1])

    epsg = get_most_accurate_epsg(x, y)
    print(int(epsg))
    testGraph = convertNodesCoordinates(testGraph, 4326, 3946)
    print(testGraph.node[1])
