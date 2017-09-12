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

from osgeo import ogr, osr

def convertCoordinates(coordinate, sourceEPSG, targetEPSG):
	sourceProjection = osr.SpatialReference()
	sourceProjection.ImportFromEPSG(sourceEPSG)
	destinationProjection = osr.SpatialReference()
	destinationProjection.ImportFromEPSG(targetEPSG)
	coordTrans = osr.CoordinateTransformation(sourceProjection, destinationProjection)
	point = ogr.Geometry(ogr.wkbPoint)
	lon, lat = coordinate
	point.AddPoint(lon,lat)
	point.Transform(coordTrans)
	return point.GetX(), point.GetY()

def batchConvertCoordinates(sourceCoordinates, sourceEPSG, targetEPSG):
	targetCoordinates = []
	sourceProjection = osr.SpatialReference()
	sourceProjection.ImportFromEPSG(sourceEPSG)
	destinationProjection = osr.SpatialReference()
	destinationProjection.ImportFromEPSG(targetEPSG)
	coordTrans = osr.CoordinateTransformation(sourceProjection, destinationProjection)
	for lon, lat in sourceCoordinates:
		point = ogr.Geometry(ogr.wkbPoint)
		point.AddPoint(lon,lat)
		point.Transform(coordTrans)
		targetCoordinates.append((point.GetX(), point.GetY()))
	return targetCoordinates