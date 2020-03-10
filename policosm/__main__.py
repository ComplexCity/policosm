#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
	extract a graph from

parameters
	graph

how it works

return


"""
import argparse
# standard python libraries
import time
from time import localtime, strftime

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
				description='''Extract road networks from your osm file''',
				epilog='''Please be patient, this can take up to 300 sec for a city wide extract''')

	parser.add_argument('osm_file', action='store', help='your .osm, .pbf, .osm.bz2 source file')
	parser.add_argument('-o', '--output', action='store', dest='outfile', default='osmRoadNetwork.gexf', help='destination graph file')
	parser.add_argument('-f', '--format', action='store', choices=['gexf', 'gml', 'graphml', 'json'], default='gexf', help='graph format to choose from gexf, gml, graphml, json and shp. Format should match your outfile extension.')
	parser.add_argument('-b', '--boundingBox', action='store', help="Retrains the graph to the provided bounding box. It takes 2 coordinates lon,lat (top left, bottom right) separated by a comma. ex: '121.434, 31.4542, 122.453, 27.554'")
	parser.add_argument('-c', '--clean', action='store_true', default=False, help="remove nodes without geographic informations and single nodes")
	parser.add_argument('-s', '--simplify', action='store_true', default=False, help="simplify path for network analysis. transform all path like into one edge. add length and keep geo measure only if distance has been calculated beforehand. Equivalent to Ramer Douglas Peucker Algorithm with an infinite epsilon")
	parser.add_argument('-d', '--distance', action='store', dest='distance', type=int, default=2154, help="calculate distance for every edge on the graph based on lat & lon")
	parser.add_argument('-v', '--verbose', action='store_true', default=False, help="display processing informations")
	parser.add_argument('-rdp', action='store_true', default=False, help="display processing informations")
	# Ramer Douglas Peucker
	arguments = parser.parse_args()

	verbose = arguments.verbose

# instantiate counter and parser and start parsing
if verbose:
	begin = localtime()
	print(strftime("%H:%M:%S", localtime()) + ' — Parsing ' + str(arguments.osm_file))
roadsNetwork = Roads()
osmParser = OSMParser(concurrency=4, coords_callback=roadsNetwork.nodes, ways_callback=roadsNetwork.edges)
osmParser.parse(arguments.osm_file)

if verbose:
	graphSummary()

# bounding box the graph is necessary
if arguments.boundingBox:
	if verbose:
		print(strftime("%H:%M:%S", localtime()) + ' — Bounding Boxing to ' + arguments.boundingBox)
	coordinates = [float(x.strip()) for x in arguments.boundingBox.split(',')]
	boundingBox(coordinates)
	if verbose:
		graphSummary()

if arguments.clean:
	if verbose:
		print(strftime("%H:%M:%S", localtime()) + ' — Cleaning the graph')
	clean()
	if verbose:
		graphSummary()

if arguments.distance:
	if verbose:
		print(strftime("%H:%M:%S", localtime()) + ' — Calculating distance the graph')
	updateEdgesWithMetricDistance(arguments.distance)

if arguments.simplify:
	if verbose:
		print(strftime("%H:%M:%S", localtime()) + ' — Simplifying path in graph')
	simplify()
	if verbose:
		graphSummary()

if verbose:
	print(strftime("%H:%M:%S", localtime()) + ' — writing ' + arguments.format + ' graph in ' + arguments.outfile)
writeGraph(arguments.format, arguments.outfile)

if verbose:
	print ('finished in',str(time.time() - time.mktime(begin)))
