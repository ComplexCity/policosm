#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	simplify roads graph created from osm file
	transform curved geographic path with multiple nodes
	with the same road level into a simple line. 

	o——o	   o——o	
		\	  /    `o  becomes  o——o
		 o———o

	if 'length' attribute in graph, update final line with 
	sum of all lines length to retain accurate length information

parameters
	graph

how it works
	1 - for all nodes with degree equals 2
	2 - create a line between previous node and next node
	3 - remove node

return
	graph simplified

'''

import networkx as nx

def simplify(graph):
	for node in graph.nodes():
		if len(graph[node].keys()) == 2:
			node1 = graph[node].keys()[0]
			node2 = graph[node].keys()[1]

			if(node1 in graph[node2]):
				continue

			if graph[node][node1]['level'] == graph[node][node2]['level']:
				attributes = graph[node][node1]
				if 'length' in attributes:
					attributes['length'] = graph[node][node1]['length'] + graph[node][node2]['length']
				graph.add_edge(node1,node2, attributes)
				graph.remove_node(node)
	return graph