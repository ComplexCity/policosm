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
from policosm.functions import *

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


def plotRoadsGraph(graph):
	data = []
	for u,v in graph.edges():
		data.append(
			go.Scattergl(
				x = [graph.node[u]['longitude'], graph.node[v]['longitude']],
				y = [graph.node[u]['latitude'], graph.node[v]['latitude']],
				mode = 'lines',
				line = my_style[graph[u][v]['level']],
				)
			)

	x,y = getCentroidFromRoadsGraph(graph)
	boundaries = getBoundaries(graph)
	width = boundaries[2]-boundaries[0]
	height = boundaries[3]-boundaries[1]
	standard = max([width,height])
	standard += standard * 0.1

	layout = go.Layout(
		showlegend=False,
		xaxis=dict(
			range=[x-standard/2, x+standard/2],
			showgrid=True,
			zeroline=False,
			showline=False,
			gridcolor='#eeeeee',
			gridwidth=1,
			linecolor='#eeeeee',
			linewidth=1
		),
		yaxis=dict(
			range=[y-standard/2, y+standard/2],
			showgrid=True,
			zeroline=False,
			showline=False,
			gridcolor='#eeeeee',
			gridwidth=1,
			linecolor='#eeeeee',
			linewidth=1
		),
		width=1000,
		height=1000	
	)

	return dict(data=data, layout=layout)

def plotRoadsGraphHTML(graph,filename,div=False, auto_open=False):
	fig = plotRoadsGraph(graph)
	output = 'div' if div else 'file' 
	plot( fig, output_type=output, filename=filename+'.html', auto_open=False)

def plotRoadsGraphPNG(graph,filename):
	fig = plotRoadsGraph(graph)
	plot( fig, auto_open=False, image='png', image_filename=filename, image_width=1000, image_height=1000)

def plotRoadsGraphNetworkx(G):
	import matplotlib.pyplot as plt
	
	eoriginal=[(u,v) for (u,v,d) in G.edges(data=True) if d['level'] >= 3]
	enew=[(u,v) for (u,v,d) in G.edges(data=True) if d['level'] < 3]

	pos={}
	for n in G.nodes():
		pos[n] = (G.node[n]['longitude'],G.node[n]['latitude'])

	# nodes
	nx.draw_networkx_nodes(G,pos,node_size=3)

	# edges
	nx.draw_networkx_edges(G,pos,edgelist=eoriginal,alpha=0.8,width=1)
	nx.draw_networkx_edges(G,pos,edgelist=enew,width=1,alpha=0.8,edge_color='r')

	# labels
	nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

	plt.show()


if __name__ == "__main__":
	plotly.offline.init_notebook_mode()
	filename = '/Volumes/Fabien/Research/cities-pictures/data/France/1-pbf/2A004.pbf'
	graph = roadsGraph(filename)
	raw_count = len(graph.edges())
	print 'raw',raw_count,'edges'
	graph = pocogeo.clean(graph)
	clean_count = len(graph.edges())
	print 'clean',clean_count,'edges',100-int(float(clean_count)/raw_count*100),'percent saved'
	graph = pocogeo.simplify(graph)
	simplified_count = len(graph.edges())
	print 'simplified',simplified_count,'edges',100-int(float(simplified_count)/raw_count*100),'percent saved'
	
	# plotRoadsGraphPNG(graph,filename.split('/')[-1].split('.')[-2])
	plotRoadsGraphNetworkx(graph)