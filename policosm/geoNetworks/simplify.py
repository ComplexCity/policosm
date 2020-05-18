#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende
"""

import logging

import geopandas as gpd
import graph_tool as gt
import pandas as pd
from more_itertools import pairwise

from policosm.geoFunctions.linestrings_operation import join_linestrings


def simplify(graph):
    for node in graph.nodes():
        if len(graph[node].keys()) == 2:
            node1 = graph[node].keys()[0]
            node2 = graph[node].keys()[1]

            if (node1 in graph[node2]):
                continue

            if graph[node][node1]['level'] == graph[node][node2]['level']:
                attributes = graph[node][node1]
                if 'length' in attributes:
                    attributes['length'] = graph[node][node1]['length'] + graph[node][node2]['length']
                graph.add_edge(node1, node2)
                graph.egdes[node1, node2].update(attributes)
                graph.remove_node(node)
    return graph


def simplify_undirected_as_dataframe(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    r"""
    Simplify an undirected graph stored in a dataframe.
    u –– current node –– v becomes
    u –– v and path [u - current node - v] is saved
    for each node of degree 2, if the inputs have the same highway than the outputs,

    Parameters
    ----------
    df : pandas dataframe
        an edge list dataframe with the following columns:
            u, v undirected couple of nodes u –– v
            osm_id, highway, level, lanes, width, bicycle, bicycle_safety, foot, foot_safety, max_speed, motorcar, geometry

    Returns
    -------
    dataframe : pandas Dataframe
       simplified Dataframe of the undirected graph
    """
    df.reset_index(inplace=True)

    g = gt.Graph(directed=False)
    osm_id = g.new_edge_property('string')
    highway = g.new_edge_property('string')
    level = g.new_edge_property('int')
    lanes = g.new_edge_property('int')
    width = g.new_edge_property('float')
    bicycle = g.new_edge_property('bool')
    bicycle_safety = g.new_edge_property('int')
    foot = g.new_edge_property('bool')
    foot_safety = g.new_edge_property('int')
    max_speed = g.new_edge_property('int')
    motorcar = g.new_edge_property('bool')
    linestring = g.new_edge_property('python::object')

    edgelist = df[
        ['u', 'v', 'osm_id', 'highway', 'level', 'lanes', 'width', 'bicycle', 'bicycle_safety', 'foot', 'foot_safety',
         'max_speed', 'motorcar', 'geometry']].values

    nodes_id = g.add_edge_list(edgelist, hashed=True,
                               eprops=[osm_id, highway, level, lanes, width, bicycle, bicycle_safety, foot, foot_safety,
                                       max_speed, motorcar, linestring])

    # we are gonna replace the original repeated nodes with a linestring
    e_path = g.new_ep('vector<int64_t>')
    for e in g.edges():
        e_path[e] = []

    vs = g.get_vertices()
    deg_2 = g.get_out_degrees(vs) == 2

    logging.debug('selecting degree 2 candidates')
    candidates = set()
    for i, v in enumerate(vs):
        if deg_2[i]:
            u = g.get_out_neighbors(v)[0]
            w = g.get_out_neighbors(v)[1]

            if u != w:
                vu, vw = g.edge(v, u), g.edge(v, w)
                if highway[vu] == highway[vw]:
                    candidates.add(v)
    logging.debug('found {} degree 2 candidates to simplify'.format(len(candidates)))

    seen = set()
    unregister_candidates = set()

    for candidate in candidates:
        if candidate in seen:
            continue

        seen.add(candidate)

        u = g.get_out_neighbors(candidate)[0]
        w = g.get_out_neighbors(candidate)[1]

        uc = g.edge(u, candidate)

        is_u_fringe, is_w_fringe = u not in candidates, w not in candidates

        us = []
        ws = []

        while not is_u_fringe:
            seen.add(u)
            us.append(u)
            neighbors = set(g.get_out_neighbors(u))
            neighbors -= seen
            if len(neighbors) > 0:
                u = neighbors.pop()
                is_u_fringe = u not in candidates
            elif u == w:
                us.pop(-1)
                u = us.pop(-1)
                unregister_candidates.add(u)
                unregister_candidates.add(w)
                is_u_fringe = True
                is_w_fringe = True
                g.remove_edge(g.edge(s=w, t=u))
            else:
                logging.debug('degree 1: we got here somehow {} {} {} {}', candidate, u, v,
                              g.get_all_neighbors(candidate))
                break

        while not is_w_fringe:
            seen.add(w)
            ws.append(w)
            neighbors = set(g.get_out_neighbors(w))
            neighbors -= seen
            if len(neighbors) > 0:
                w = neighbors.pop()
                is_w_fringe = w not in candidates
            else:
                logging.debug('degree 1: we got here somehow {} {} {} {}', candidate, u, v,
                              g.get_all_neighbors(candidate))
                break

        if is_u_fringe and is_w_fringe:
            path = [u] + list(reversed(us)) + [candidate] + ws + [w]
            linestrings = [linestring[g.edge(a, b)] for a, b in pairwise(path)]
            joined_linestring = join_linestrings(linestrings)
            if joined_linestring is None:
                path = list(reversed(path))
                linestrings = [linestring[g.edge(a, b)] for a, b in pairwise(path)]
                joined_linestring = join_linestrings(linestrings)

            e = g.add_edge(source=path[0], target=path[-1])
            linestring[e] = joined_linestring
            e_path[e] = [int(nodes_id[node]) for node in path]
            osm_id[e], highway[e], level[e], lanes[e], width[e], bicycle[e], bicycle_safety[e], foot[e], foot_safety[e], \
            max_speed[e], motorcar[e] = osm_id[uc], highway[uc], level[uc], lanes[uc], width[uc], bicycle[uc], \
                                        bicycle_safety[uc], \
                                        foot[uc], foot_safety[uc], max_speed[uc], motorcar[uc]
        else:
            logging.error('unexpected behavior, source={0}, target={1}, candidate={2}, us={3}, ws={4}', u, w, us, ws)

    unseen = candidates - seen
    if len(unseen) > 0:
        logging.debug(
            'Network scan after degree 2 simplification not finished: candidates {0} have not been examined'.format(
                unseen))

    candidates -= unregister_candidates
    g.remove_vertex(list(candidates))

    logging.debug(' linestring path')
    edges_tuples = []
    for e in g.edges():
        source, target, path = nodes_id[e.source()], nodes_id[e.target()], e_path[e]
        if len(path) == 0:
            path = [source, target]
        else:
            path = [int(i) for i in path]

        e_tuples = (g.edge_index[e], source, target, path,
                    osm_id[e], highway[e], level[e], lanes[e], width[e], bicycle[e], bicycle_safety[e], foot[e],
                    foot_safety[e], max_speed[e], motorcar[e], linestring[e])
        edges_tuples.append(e_tuples)

    df_edges_simplified = pd.DataFrame.from_records(edges_tuples, index='edge_id',
                                                    columns=['edge_id', 'u', 'v', 'path', 'osm_id', 'highway',
                                                             'level', 'lanes', 'width', 'bicycle', 'bicycle_safety',
                                                             'foot', 'foot_safety', 'max_speed', 'motorcar',
                                                             'geometry'])

    df_edges_simplified.osm_id = df_edges_simplified.osm_id.str.split('-').str[0]
    df_edges_simplified = gpd.GeoDataFrame(df_edges_simplified, geometry='geometry')
    df_edges_simplified.crs = df.crs
    return df_edges_simplified


def simplify_directed_as_dataframe(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    r"""
    Simplify a directed graph stored in a dataframe.
    u -> current node -> v becomes
    u -> v and path [u -> current node -> v] is saved
    for each node of degree 4 or 2, if the inputs have the same highway than the outputs,

    Parameters
    ----------
    df : pandas dataframe
        an edge list dataframe with the following columns:
            u, v directed couple of nodes u -> v
            osm_id, highway, level, lanes, width, bicycle, bicycle_safety, foot, foot_safety, max_speed, motorcar, geometry

    Returns
    -------
    dataframe : pandas Dataframe
       simplified Dataframe of the directed graph
    """
    df.reset_index(inplace=True)

    g = gt.Graph(directed=True)
    osm_id = g.new_edge_property('string')
    highway = g.new_edge_property('string')
    level = g.new_edge_property('int')
    lanes = g.new_edge_property('int')
    width = g.new_edge_property('float')
    bicycle = g.new_edge_property('bool')
    bicycle_safety = g.new_edge_property('int')
    foot = g.new_edge_property('bool')
    foot_safety = g.new_edge_property('int')
    max_speed = g.new_edge_property('int')
    motorcar = g.new_edge_property('bool')
    linestring = g.new_edge_property('python::object')

    edgelist = df[
        ['u', 'v', 'osm_id', 'highway', 'level', 'lanes', 'width', 'bicycle', 'bicycle_safety', 'foot', 'foot_safety',
         'max_speed', 'motorcar', 'geometry']].values

    nodes_id = g.add_edge_list(edgelist, hashed=True,
                               eprops=[osm_id, highway, level, lanes, width, bicycle, bicycle_safety, foot, foot_safety,
                                       max_speed, motorcar, linestring])

    # we are gonna replace the original repeated nodes with a linestring
    e_path = g.new_ep('vector<int64_t>')
    for e in g.edges():
        e_path[e] = []

    vs = g.get_vertices()
    in_out_deg_2 = (g.get_in_degrees(vs) == 2) & (g.get_out_degrees(vs) == 2)

    logging.debug('selecting degree 4 candidates')
    candidates = set()
    for i, v in enumerate(vs):
        if in_out_deg_2[i]:
            ns = list(set(g.get_all_neighbors(v)))
            if len(ns) == 2:
                u, w = ns[0], ns[1]
                uv, vw, wv, vu = g.edge(u, v), g.edge(v, w), g.edge(w, v), g.edge(v, u)
                if highway[uv] == highway[vw] and highway[wv] == highway[vu]:
                    candidates.add(v)
    logging.debug('found {} degree 4 candidates to simplify'.format(len(candidates)))

    seen = set()
    unregister_candidates = set()

    for i, candidate in enumerate(candidates):
        if i == 100000:
            logging.debug('100000 degree 4 candidates')
        if candidate in seen:
            continue

        seen.add(candidate)

        u, w = g.get_out_neighbors(candidate)
        is_u_fringe, is_w_fringe = u not in candidates, w not in candidates

        cu, cw = g.edge(candidate, u), g.edge(candidate, w)

        us = []
        ws = []

        while not is_u_fringe:
            seen.add(u)
            us.append(u)
            neighbors = set(g.get_out_neighbors(u))
            neighbors -= seen
            if len(neighbors) > 0:
                u = neighbors.pop()
                is_u_fringe = u not in candidates
            elif u == w:
                us.pop(-1)
                u = us.pop(-1)
                unregister_candidates.add(u)
                unregister_candidates.add(w)
                is_u_fringe = True
                is_w_fringe = True
                g.remove_edge(g.edge(s=u, t=w))
                g.remove_edge(g.edge(s=w, t=u))
            else:
                logging.debug('degree 2: we got here somehow {} {} {} {}', candidate, u, v,
                              g.get_all_neighbors(candidate))
                break

        while not is_w_fringe:
            seen.add(w)
            ws.append(w)
            neighbors = set(g.get_out_neighbors(w))
            neighbors -= seen
            if len(neighbors) > 0:
                w = neighbors.pop()
                is_w_fringe = w not in candidates
            else:
                logging.debug('degree 2: we got here somehow {} {} {} {}', candidate, u, v,
                              g.get_all_neighbors(candidate))
                break

        if is_u_fringe and is_w_fringe:
            e = g.add_edge(source=u, target=w)
            path = [u] + list(reversed(us)) + [candidate] + ws + [w]
            e_path[e] = [int(nodes_id[node]) for node in path]
            linestrings = [linestring[g.edge(a, b)] for a, b in pairwise(path)]
            linestring[e] = join_linestrings(linestrings)
            osm_id[e], highway[e], level[e], lanes[e], width[e], bicycle[e], bicycle_safety[e], foot[e], foot_safety[e], \
            max_speed[e], motorcar[e] = osm_id[cw], highway[cw], level[cw], lanes[cw], width[cw], bicycle[cw], \
                                        bicycle_safety[cw], \
                                        foot[cw], foot_safety[cw], max_speed[cw], motorcar[cw]

            e = g.add_edge(source=w, target=u)
            path = [w] + list(reversed(ws)) + [candidate] + us + [u]
            e_path[e] = [int(nodes_id[node]) for node in path]
            linestrings = [linestring[g.edge(a, b)] for a, b in pairwise(path)]
            linestring[e] = join_linestrings(linestrings)
            osm_id[e], highway[e], level[e], lanes[e], width[e], bicycle[e], bicycle_safety[e], foot[e], foot_safety[e], \
            max_speed[e], motorcar[e] = osm_id[cu], highway[cu], level[cu], lanes[cu], width[cu], bicycle[cu], \
                                        bicycle_safety[cu], \
                                        foot[cu], foot_safety[cu], max_speed[cu], motorcar[cu]

        else:
            logging.debug(
                'unexpected behavior, source={0}, target={1}, candidate={2}, us={3}, ws={4}'.format(u, w, candidate, us,
                                                                                                    ws))

    unseen = candidates - seen
    if len(unseen) > 0:
        logging.debug(
            'Network scan after degree 4 simplification uncomplete: candidates {0} have not been examined'.format(
                unseen))

    candidates -= unregister_candidates
    g.remove_vertex(list(candidates))

    vs = g.get_vertices()
    in_out_deg_1 = (g.get_in_degrees(vs) == 1) & (g.get_out_degrees(vs) == 1)

    logging.debug('selecting degree 2 candidates')
    candidates = set()
    for i, v in enumerate(vs):
        if in_out_deg_1[i]:
            u = g.get_in_neighbors(v)[0]
            w = g.get_out_neighbors(v)[0]

            if u != w:
                uv, vw = g.edge(u, v), g.edge(v, w)
                if highway[uv] == highway[vw]:
                    candidates.add(v)
    logging.debug('found {} degree 2 candidates to simplify'.format(len(candidates)))

    seen = set()
    unregister_candidates = set()

    for candidate in candidates:
        if candidate in seen:
            continue

        seen.add(candidate)

        u = g.get_in_neighbors(candidate)[0]
        w = g.get_out_neighbors(candidate)[0]

        uc = g.edge(u, candidate)

        is_u_fringe, is_w_fringe = u not in candidates, w not in candidates

        us = []
        ws = []

        while not is_u_fringe:
            seen.add(u)
            us.append(u)
            neighbors = set(g.get_in_neighbors(u))
            neighbors -= seen
            if len(neighbors) > 0:
                u = neighbors.pop()
                is_u_fringe = u not in candidates
            elif u == w:
                us.pop(-1)
                u = us.pop(-1)
                unregister_candidates.add(u)
                unregister_candidates.add(w)
                is_u_fringe = True
                is_w_fringe = True
                g.remove_edge(g.edge(s=w, t=u))
            else:
                logging.debug('degree 1: we got here somehow {} {} {} {}', candidate, u, v,
                              g.get_all_neighbors(candidate))
                break

        while not is_w_fringe:
            seen.add(w)
            ws.append(w)
            neighbors = set(g.get_out_neighbors(w))
            neighbors -= seen
            if len(neighbors) > 0:
                w = neighbors.pop()
                is_w_fringe = w not in candidates
            else:
                logging.debug('degree 1: we got here somehow {} {} {} {}', candidate, u, v,
                              g.get_all_neighbors(candidate))
                break

        if is_u_fringe and is_w_fringe:
            e = g.add_edge(source=u, target=w)
            path = [u] + list(reversed(us)) + [candidate] + ws + [w]
            e_path[e] = [int(nodes_id[node]) for node in path]
            linestrings = [linestring[g.edge(a, b)] for a, b in pairwise(path)]
            linestring[e] = join_linestrings(linestrings)
            osm_id[e], highway[e], level[e], lanes[e], width[e], bicycle[e], bicycle_safety[e], foot[e], foot_safety[e], \
            max_speed[e], motorcar[e] = osm_id[uc], highway[uc], level[uc], lanes[uc], width[uc], bicycle[uc], \
                                        bicycle_safety[uc], \
                                        foot[uc], foot_safety[uc], max_speed[uc], motorcar[uc]
        else:
            logging.error('unexpected behavior, source={0}, target={1}, candidate={2}, us={3}, ws={4}', u, w, us, ws)

    unseen = candidates - seen
    if len(unseen) > 0:
        logging.debug(
            'Network scan after degree 2 simplification not finished: candidates {0} have not been examined'.format(
                unseen))

    candidates -= unregister_candidates
    g.remove_vertex(list(candidates))

    logging.debug(' linestring path')
    edges_tuples = []
    for e in g.edges():
        source, target, path = nodes_id[e.source()], nodes_id[e.target()], e_path[e]
        if len(path) == 0:
            path = [source, target]
        else:
            path = [int(i) for i in path]

        e_tuples = (g.edge_index[e], source, target, path,
                    osm_id[e], highway[e], level[e], lanes[e], width[e], bicycle[e], bicycle_safety[e], foot[e],
                    foot_safety[e], max_speed[e], motorcar[e], linestring[e])
        edges_tuples.append(e_tuples)

    df_edges_simplified = pd.DataFrame.from_records(edges_tuples, index='edge_id',
                                                    columns=['edge_id', 'u', 'v', 'path', 'osm_id', 'highway',
                                                             'level', 'lanes', 'width', 'bicycle', 'bicycle_safety',
                                                             'foot', 'foot_safety', 'max_speed', 'motorcar',
                                                             'geometry'])

    df_edges_simplified.osm_id = df_edges_simplified.osm_id.str.split('-').str[0]
    df_edges_simplified = gpd.GeoDataFrame(df_edges_simplified, geometry='geometry')
    df_edges_simplified.crs = df.crs
    return df_edges_simplified
