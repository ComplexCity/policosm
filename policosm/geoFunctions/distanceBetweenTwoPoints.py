#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in July 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does

parameters

how it works

return
CAREFUL THE UNIT IS THE ONE OF THE PROJECTION SYSTEM CHOOSE A METER UNIT
'''

from osgeo import ogr, osr

from policosm.geoFunctions.convertCoordinates import *

def distanceBetweenTwoPoints(point1,point2, sourceEPSG = 4326, targetEPSG = None):
	lon1, lat1 = point1
	lon2, lat2 = point2
	if targetEPSG is not None:
		(lon1, lat1), (lon2, lat2) = batchConvertCoordinates([(lon1, lat1), (lon2, lat2)], sourceEPSG, targetEPSG)
	line = ogr.Geometry(ogr.wkbLineString)
	line.AddPoint(lon1,lat1)
	line.AddPoint(lon2,lat2)
	return line.Length()


if __name__ == "__main__":
	coordinate1 = (121.457297322, 31.2717232641)
	coordinate2 = (121.451576522, 31.2726585258)
	print (convertCoordinates(coordinate1, 4326, 4479))
	print (distanceBetweenTwoPoints(coordinate1, coordinate2))
	print (distanceBetweenTwoPoints(coordinate1, coordinate2, targetEPSG=4490))
	print (distanceBetweenTwoPoints(coordinate1, coordinate2, targetEPSG=4479))