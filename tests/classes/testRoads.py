#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende
'''
import pytest

@pytest.fixture

def roadsData():
	from policosm.classes import Roads
	import networkx as nx 
	graph = nx.Graph()
	roads = Roads()
	graph.add_node(1,longitude=1.0, latitude=1.0)
	graph.add_node(2,longitude=2.0, latitude=2.0)
	graph.add_edge(1, 2,osmid=3,highway='residential',level=3, lanes=1, oneway=False, footway=False, bicycle=False)

	roads.nodes([[1,1.0,1.0],[2,2.0,2.0]])
	roads.edges([[3,{'highway':'residential', 'lanes':'yes'},[1,2]]])
	return graph, roads.graph 

class Test_Roads_class:
	def test_nodes(self, roadsData):
		g1, g2 = roadsData
		nl1 = list(g1.nodes(data=True))
		nl2 = list(g2.nodes(data=True))
		d1 = dict(nl1)
		d2 = dict(nl2)
		assert d1 == d2

	def test_edges(self, roadsData):
		from policosm.classes import Roads
		import networkx as nx 
		roads = Roads(verbose=False)
		roads.nodes([[1,1.0,1.0],[2,2.0,2.0]])

		# ———— OSMID RULE ——————
		roads.edges([[2,{'highway':'road'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert u == 1 and v == 2 and data['osmid'] == 2

		# ———— BICYCLE RULE ——————
		roads.edges([[3,{'highway':'road','bicycle':'yes'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['bicycle'] == True
		roads.edges([[4,{'highway':'road','bicycle':'designated'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['bicycle'] == True
		roads.edges([[5,{'highway':'cycleway'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['bicycle'] == True
		roads.edges([[6,{'highway':'cyleway'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['bicycle'] == True
		roads.edges([[2,{'highway':'road'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['bicycle'] == False

		# ———— FOOTWAY RULE ——————
		roads.edges([[7,{'highway':'road','foot':'yes'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['footway'] == True
		roads.edges([[8,{'highway':'pedestrian'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['footway'] == True
		roads.edges([[9,{'highway':'footway'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['footway'] == True
		roads.edges([[2,{'highway':'road'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['footway'] == False

		# ———— ONEWAY RULE ——————
		roads.edges([[10,{'highway':'road', 'oneway':'yes'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['oneway'] == True
		roads.edges([[2,{'highway':'road'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['footway'] == False

		# ———— LANES RULE ——————
		roads.edges([[11,{'highway':'road', 'lanes':'3'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['lanes'] == 3
		roads.edges([[12,{'highway':'road', 'lanes':'3 lignes'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['lanes'] == 3
		roads.edges([[13,{'highway':'road', 'lanes':'two'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['lanes'] == 1
		
		# ———— HIGHWAY RULE ——————	
		roads.edges([[14,{'highway':'路'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['highway'] == 'unclassified'
		roads.edges([[2,{'highway':'road'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['highway'] == 'road'

		# ———— LEVELS RULE ——————	
		roads.edges([[2,{'highway':'demolished'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 0
		roads.edges([[2,{'highway':'stairway'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 1
		roads.edges([[2,{'highway':'footway'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 2
		roads.edges([[2,{'highway':'residential'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 3
		roads.edges([[2,{'highway':'tertiary'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 4
		roads.edges([[2,{'highway':'secondary'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 5
		roads.edges([[2,{'highway':'primary'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 6
		roads.edges([[2,{'highway':'trunk'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 7
		roads.edges([[2,{'highway':'motorway'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 8
		roads.edges([[14,{'highway':'路'},[1,2]]])
		u,v, data = roads.graph.edges(data=True)[0]
		assert data['level'] == 3

		# ———— APPLY TO THE WHOLE WAY RULE ——————
		roads.edges([[2,{'highway':'road'},[1,2]]])
		assert len(roads.graph.edges()) == 1
		roads.nodes([[3,1.0,1.0],[4,2.0,2.0]])
		roads.edges([[2,{'highway':'road'},[1,2,3,4]]])
		assert len(roads.graph.edges()) == 3

		# ———— TEST GRAPH IDENTITY —————— 
		import networkx.algorithms.isomorphism as iso
		g1, g2 = roadsData
		eKeys = ['lanes', 'osmid', 'footway', 'level', 'bicycle', 'oneway', 'highway']
		eValues = [1, 3, False, 3, False, False, 'residential']
		em = iso.categorical_edge_match(eKeys, eValues)
		assert nx.is_isomorphic(g1, g2, edge_match=em)

if __name__ == "__main__":
	test = TestRoads()
	test.test_nodes(roadsData())
	test.test_edges(roadsData())

