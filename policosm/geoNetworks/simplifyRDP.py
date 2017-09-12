#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	Apply Ramer-Douglas-Peucker algorithm to graph

	o——o	   o——o				o			o
		\	  /    `o  becomes    \	      /	 `o
		 o———o						 o——o

	for more information see https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm

parameters
	graph
	epsilon (distance threshold from original curve and simplified curve)
	
how it works
	1 - get a list of all lines with only degree 2 nodes
	2 - apply rdp algorthm to lines
	3 - remove nodes the rdp algorithm did not retain  

return
	graph minus nodes not selected by rdp

'''

import networkx as nx
import numpy as np
from rdp import rdp

def detectLinesWithDepthFirstSearch(G):
	lines = []
	visited = set()

	for u,v in G.edges():
		if u == v:
			G.remove_edge(u,v)

	for start in G.nodes():

		if start in visited:
			continue

		if len(G[start]) != 2:
			continue

		left = G[start].keys()[0]
		right = G[start].keys()[1]

		if G[start][left]['level']!= G[start][right]['level']:
			continue

		visited.add(start)
		level = G[start][left]['level']
		line = []
		path = [start]
		stack = [(start,iter(G[start]))]
		while stack:
			parent, children = stack[-1]

			if len(path) > 1 and len(stack) == 1:
				line.append(path)
				path = [start]
			try:
				child = next(children)
				if child not in visited and G[parent][child]['level'] == level and G.degree(child) == 2:
					path.append(child)
					visited.add(child)
					stack.append((child,iter(G[child])))
			except StopIteration:
				stack.pop()
		
		if len(line) == 0:
			line = [[start],[start]]
		elif len(line) == 1:
			line.append([start])

		
		farleft = G[line[0][-1]].keys()[0] if G[line[0][-1]].keys()[1] in visited else G[line[0][-1]].keys()[1]
		farright = G[line[1][-1]].keys()[0] if G[line[1][-1]].keys()[1] in visited or G[line[1][-1]].keys()[1] == farleft else G[line[1][-1]].keys()[1]
		if G[line[0][-1]][farleft]['level'] == level:
			line[0].append(farleft)
		if G[line[1][-1]][farright]['level'] == level:
			line[1].append(farright)
		
		line[0].reverse()
		lines.append(line[0]+line[1][1:])
	return lines


def rdp_line(path, epsilon):
	return rdp(np.array(path).reshape(len(path)/2, 2),epsilon=epsilon)


def simplify_with_rdp(G, epsilon=0.00025):
	for line in detectLinesWithDepthFirstSearch(G):
		
		# apply RDP to each line 
		path = []
		for node in line:
			path.append(G.node[node]['longitude'])
			path.append(G.node[node]['latitude'])
		path = rdp_line(path, epsilon)
		
		# create the final line from the new path
		newline = []
		for longitude, latitude in path:
			for node in line:
				if G.node[node]['longitude'] == longitude and G.node[node]['latitude'] == latitude:
					newline.append(node)
		
		# redesign the conectivity according to the new line but keeping the length accurate
		source = newline[0]
		attributes = G[source][line[1]]
		length = 0
		for i in range (1,len(line)):
			target = line[i]
			if 'length' in attributes:
				length += G[line[i-1]][target]['length']
			if target in newline:
				if 'length' in attributes:
					attributes['length'] = length
					length = 0
				try:
					edge = G[source][target]
				except KeyError:
					G.add_edge(source,target,attributes)
				source = target

		for node in line:
			if node not in newline:
				G.remove_node(node)
	return G
