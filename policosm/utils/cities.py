#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in June 2016 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	define integer roads levels according to highway tag in open street map
'''

cities = {'France':[
	('Megève','74173'),
	('Miribel','01249'),
	('Marseille','13055'),
	('Grenoble','38185')
	]
}

def getCities():
	for country in cities:
		print country
		for name, code in cities[country]:
			print '\t',name, code

def getCitiesPBF(city):
	for country in cities:
		for name, code in cities[country]:
			if name.lower() == city.lower():
				return code+'.pbf'