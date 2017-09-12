#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	extract a graph from 

parameters
	graph

how it works

return
	

'''

import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

from imposm.parser import OSMParser
import networkx as nx
from policosm.classes.transportation import Transportation

def transportationGraph(filename):
	transportation = Transportation()
	osmParser = OSMParser(concurrency=4, nodes_callback=transportation.nodes, ways_callback=transportation.ways, relations_callback=transportation.relations)
	osmParser.parse(filename)
	return transportation.info()

if __name__ == "__main__":
	print transportationGraph('../tests/69123.pbf')
