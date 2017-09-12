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

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from policosm.utils.projections import *

projections = {'France' : FranceProjections, 'USA':USAProjections}

def epsgFromCoordinates(country, longitude, latitude):
    candidateProjection = []
    candidateCenter = []
    for projection in projections[country]:
        lat1 = projection['lat1']
        lat2 = projection['lat2']
        lon1 = projection['lon1']
        lon2 = projection['lon2']
        minLat = min([lat1, lat2])
        maxLat = max([lat1, lat2])
        minLon = min([lon1, lon2])
        maxLon = max([lon1, lon2])
        if minLat < latitude and latitude < maxLat and minLon < longitude and longitude < maxLon:
            candidateProjection.append(projection['epsg'])
            candidateCenter.append(abs(lat1 - lat2))
    closest = 100

    if len(candidateProjection) == 1:
        return candidateProjection[0]
    elif len(candidateProjection) > 1: # find the closest candidate
        for i in range(0, len(candidateProjection)):
            if abs(candidateCenter[i] - latitude) < closest:
                closest = abs(candidateCenter[i] - latitude)
                finalProjection = candidateProjection[i]
        return finalProjection
    else:
        print 'Not Found!'
        print latitude
        print longitude
        return ''