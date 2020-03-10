# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point


def calcul (graph,times,to_visit,temps_max) :
    next_visits = []
    for k in range (len(to_visit)) :
        node = to_visit[k]
        neighbors = list(graph[node])

        for p in range (len(neighbors)) :
            arrival = neighbors[p]
            datas = graph.get_edge_data(node,arrival)
            les_temps = []
            for key,value in datas.items() :
                les_temps.append(value['time_travel'])

            add_time = min(les_temps)
            
            time_travel = times[node] + add_time
            if (not (arrival in times)) :
                if time_travel > temps_max :
                    continue
                else :
                    times[arrival] = time_travel
                    if arrival in next_visits :
                        continue
                    else :
                        next_visits.append(arrival)
                    
            else :
                if time_travel >= times[arrival] :
                    continue
                else :
                    if time_travel > temps_max :
                        continue
                    else :
                        times[arrival] = time_travel
                        if arrival in next_visits :
                            continue
                        else :
                            next_visits.append(arrival)

    return times,next_visits

def continuer (k, times, to_visit,csv) :
    for p in range (k) :
        times, to_visit = calcul(times,to_visit,temps_max)
        print 'times', len(times), 'to_visit', len(to_visit)
        csv.write(str(len(to_visit)))
        csv.write('\n')
    return times, to_visit

def modifier (times,graph) :
    dictionnary = {}
    for key,value in times.items() :
        dictionnary[key] = {'Travelled' : True}
    print 'On va modifier', len(dictionnary), 'noeuds'
    nx.set_node_attributes(graph,dictionnary)
    return graph

#times, to_visit = continuer (1000, times, to_visit,csv)

def application (depart_node, graph = None, isfilename = False, filename = None) :

    if isfilename :
        to_graph = nx.read_gexf(filename)
    else :
        to_graph = graph

    to_add = {}
    temps_max = 0.5 #heure
    suivi = []
    steps = []

    times={depart_node:0}
    to_visit = [depart_node]

    while len(to_visit) != 0 :
        times, to_visit = calcul(to_graph,times,to_visit,temps_max)
        suivi.append(len(to_visit))
        steps.append(len(steps)+1)

    plt.plot(steps,suivi)
    plt.show()

    fig, ax = plt.subplots()

    colors = [5,10,15,20,25,30]
    pre_polygons = [ [] for k in range (len(colors))]
    patches = []

    the_longitudes = nx.get_node_attributes(to_graph,'longitude')
    the_latitudes = nx.get_node_attributes(to_graph,'latitude')

    pre_buffer = [ [] for k in range (len(colors)) ]

    for key,value in times.items() :
        if value < 5.0/60.0 :
            to_add[key] = {'Maximum time to access' : 05, 'Travelled' : True, 'color': '#0080FF', 'Minimum time' : value}
            pre_polygons[0].append( (the_longitudes[key], the_latitudes[key]) )
            pre_buffer[0].append( Point(the_longitudes[key], the_latitudes[key]).buffer( min(0.001, (temps_max - value)*3.0)) )
        elif value < 10.0/60.0 :
            to_add[key] = {'Maximum time to access' : 10, 'Travelled' : True, 'color': '#0080FF', 'Minimum time' : value}
            pre_polygons[1].append( (the_longitudes[key], the_latitudes[key]) )
            pre_buffer[1].append( Point(the_longitudes[key], the_latitudes[key]).buffer( min(0.001, (temps_max - value)*3.0)) )
        elif value < 15.0/60.0 :
            to_add[key] = {'Maximum time to access' : 15, 'Travelled' : True, 'color': '#0080FF', 'Minimum time' : value}
            pre_polygons[2].append( (the_longitudes[key], the_latitudes[key]) )
            pre_buffer[2].append( Point(the_longitudes[key], the_latitudes[key]).buffer( min(0.001, (temps_max - value)*3.0)) )
        elif value < 20.0/60.0 :
            to_add[key] = {'Maximum time to access' : 20, 'Travelled' : True, 'color': '#0080FF', 'Minimum time' : value}
            pre_polygons[3].append( (the_longitudes[key], the_latitudes[key]) )
            pre_buffer[3].append( Point(the_longitudes[key], the_latitudes[key]).buffer( min(0.001, (temps_max - value)*3.0)) )
        elif value < 25.0/60.0 :
            to_add[key] = {'Maximum time to access' : 25, 'Travelled' : True, 'color': '#0080FF', 'Minimum time' : value}
            pre_polygons[4].append( (the_longitudes[key], the_latitudes[key]) )
            pre_buffer[4].append( Point(the_longitudes[key], the_latitudes[key]).buffer( min(0.001, (temps_max - value)*3.0)) )
        elif value < 30.0/60.0 :
            to_add[key] = {'Maximum time to access' : 30, 'Travelled' : True, 'color': '#0080FF', 'Minimum time' : value}
            pre_polygons[5].append( (the_longitudes[key], the_latitudes[key]) )
            pre_buffer[5].append( Point(the_longitudes[key], the_latitudes[key]).buffer( min(0.001, (temps_max - value)*3.0)) )
        else :
            continue

    pre_buffer[1] = pre_buffer[0] + pre_buffer[1]
    pre_buffer[2] = pre_buffer[0] + pre_buffer[1] + pre_buffer[2]
    pre_buffer[3] = pre_buffer[0] + pre_buffer[1] + pre_buffer[2] + pre_buffer[3]
    pre_buffer[4] = pre_buffer[0] + pre_buffer[1] + pre_buffer[2] + pre_buffer[3] + pre_buffer[4]
    pre_buffer[5] = pre_buffer[0] + pre_buffer[1] + pre_buffer[2] + pre_buffer[3] + pre_buffer[4] + pre_buffer[5]

    nodeis = list(to_graph.nodes)

    for k in range (len(nodeis)) :

        if (nodeis[k] in to_add) or (to_graph.nodes[nodeis[k]]['utilisation'] == 'Boundary') :
            continue
        else :
            to_add[nodeis[k]] = { 'Travelled' : False, 'color': '#FF0000'}

    #nx.set_node_attributes(to_graph,to_add)

    return to_add

if __name__ == "__main__":
    os.chdir('/home/alex/Bureau/data-test')
    graphs = application ('35721385', graph = None, isfilename = True, filename = '/home/alex/Bureau/Toulouse-21-8tr.gexf')
