#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	clean roads graph created from osm file

parameters
	graph

how it works
	1 - remove nodes without geographic informations (latitude or longitude)
	2 - remove self referencing edges (loop on itself)
	3 - remove isolated nodes (degree is 0 )

return
	graph minus alone or non-conform nodes

'''


def clean(graph):
	
	flagged_for_delation = []

	#remove node without complete geographic information
	for node in graph.nodes():
		if 'latitude' not in graph.node[node] or 'longitude' not in graph.node[node]:
			flagged_for_delation.append(node)
			

	# remove self referencing edges
	for u,v in graph.edges():
		if u == v:
			flagged_for_delation.append((u,v))

	# remove nodes with degree 0
	for node in graph.nodes():
		if len(graph[node].keys()) == 0:
			flagged_for_delation.append(node)


	for element in flagged_for_delation:
		if type(element) is tuple:
			u,v = element
			graph.remove_edge(u,v)
		else:
			graph.remove_node(element)

	return graph
