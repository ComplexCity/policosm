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
import sys
sys.path.insert(0, '/Users/fabien/workspace/github/policosm')

import plotly
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import networkx as nx
import colorlover as cl

from policosm.extractors.roadsGraph import *
import policosm.geo_networks as pocogeo
from  policosm.functions.getCentroidFromRoadsGraph import *

my_colors = cl.scales['9']['seq']['Purples']
my_style = {
	0:dict(
		color=my_colors[0],
		width=1
	),
	1:dict(
		color=my_colors[1],
		width=1
	),
	2:dict(
		color=my_colors[2],
		width=1
	),	
	3:dict(
		color=my_colors[3],
		width=1
	),
	4:dict(
		color=my_colors[4],
		width=1
	),
	5:dict(
		color=my_colors[5],
		width=1
	),
	6:dict(
		color=my_colors[6],
		width=2
	),
	7:dict(
		color=my_colors[7],
		width=2
	),
	8:dict(
		color=my_colors[8],
		width=2
	)
}


def plotRoadsGraphMapbox(graph,filename):

	data = []
	for u,v in graph.edges():
		data.append(
			go.Scattermapbox(
				lon = [graph.node[u]['longitude'], graph.node[v]['longitude']],
				lat = [graph.node[u]['latitude'], graph.node[v]['latitude']],
				mode = 'lines+markers',
				line = my_style[graph[u][v]['level']]
				# marker = dict(
				# 	size=4,
    #         		opacity=0.7
				# )
				),
			)

	x,y = getCentroidFromRoadsGraph(graph)
	layout = go.Layout(
    	autosize=True,
	    hovermode='closest',
	    showlegend=False,
	    mapbox=dict(
	        accesstoken='pk.eyJ1Ijoic2hhbmdkYWVtb24iLCJhIjoiZjJRcmZGayJ9._dYrpwwYABAtlrxIfXUE1A',
	        style='mapbox://styles/shangdaemon/ciyv9wgdq002e2rmazybmr7g8',
	        bearing=0,
	        center=dict(
	            lat=y,
	            lon=x
	        ),
	        pitch=0,
	        zoom=12
	    ),
	)

	fig = dict(data=data, layout=layout)
	plot(fig, filename=filename+'.html', validate=False)

def plotRoadsGraphMap(graph,filename):

	data = []
	for u,v in graph.edges():
		data.append(
			go.Scattermapbox(
				lon = [graph.node[u]['longitude'], graph.node[v]['longitude']],
				lat = [graph.node[u]['latitude'], graph.node[v]['latitude']],
				mode = 'lines+markers',
				line = my_style[graph[u][v]['level']]
				# marker = dict(
				# 	size=4,
    #         		opacity=0.7
				# )
				),
			)

	x,y = getCentroidFromRoadsGraph(graph)
	layout = go.Layout(
		showlegend=False,
		geo = dict(
			showland = True,
			landcolor = 'rgb(243, 243, 243)',
			countrycolor = 'rgb(204, 204, 204)',
			projection=dict(
				type='conic conformal'  
				)
			),
		)
	fig = dict(data=data, layout=layout)
	plot(fig, filename=filename+'.html', validate=False)

if __name__ == "__main__":
	plotly.offline.init_notebook_mode()
	filename = '/Volumes/Fabien/Research/cities-pictures/data/France/1-pbf/2A001.pbf'
	graph = roadsGraph(filename)
	raw_count = len(graph.edges())
	print 'raw',raw_count,'edges'
	graph = pocogeo.clean(graph)
	clean_count = len(graph.edges())
	print 'clean',clean_count,'edges',100-int(float(clean_count)/raw_count*100),'percent saved'
	graph = pocogeo.simplify(graph)
	simplified_count = len(graph.edges())
	print 'simplified',simplified_count,'edges',100-int(float(simplified_count)/raw_count*100),'percent saved'
	
	plotRoadsGraphMap(graph,filename.split('/')[-1].split('.')[-2])
