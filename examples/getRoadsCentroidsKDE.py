# coding=utf-8
import os
import networkx as nx
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from policosm import simplify, epsgFromCoordinates, convertNodesCoordinates, getCentroidsFromRoadsGraph
from policosm.functions.getKernelDensityEstimationForDifferentGrids import getKernelDensityEstimationForDifferentGrids


def convertGraphCoord(graph):
    epsg_node = graph.node[graph.node.keys()[0]]
    longitude, latitude = epsg_node['longitude'], epsg_node['latitude']

    epsg = epsgFromCoordinates('France', longitude, latitude)
    return convertNodesCoordinates(graph, 4326, int(epsg))


#  removes level two edges from graph (services, ..)
def removeLevelTwoEdges(graph):
    level_two_edges = [(u, v) for (u, v, d) in graph.edges(data=True) if d['level'] == 2]
    graph.remove_edges_from(level_two_edges)

    return graph


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    rel_path = "data/Saint-Malo.gexf"
    file_path = os.path.join(script_dir, rel_path)

    graph = nx.read_gexf(path=file_path)
    graph = simplify(graph)
    graph = convertGraphCoord(graph)
    graph = removeLevelTwoEdges(graph)
    roads_centroids = getCentroidsFromRoadsGraph(graph)
    kernel, positions, xy, bbox, bandwidth = getKernelDensityEstimationForDifferentGrids(
        roads_centroids, metric='euclidean', optimizeBandwidth=True, bwmin=10, bwmax=100, grid_sizes=[100, 250, 500])
    fig = plt.figure(figsize=(40, 10))
    gs = gridspec.GridSpec(1, 3)

    plt.subplot(gs[0])
    title = 'Roads KDE\nbw: ' + str(bandwidth) + ' 100m'
    plt.title(title, x=0.5, y=0.92, fontsize=12)
    k_pos1 = np.exp(kernel.score_samples(zip(*positions[0])))
    kde1 = np.reshape(k_pos1.T, xy[0][0].shape)
    plt.imshow(np.rot90(kde1), cmap=plt.cm.YlOrBr, extent=bbox)
    plt.contour(xy[0][0], xy[0][1], kde1, 5, colors='k', linewidths=0.6)

    plt.subplot(gs[1])
    title = 'Roads KDE\nbw: ' + str(bandwidth) + ' 250m'
    plt.title(title, x=0.5, y=0.92, fontsize=12)
    k_pos2 = np.exp(kernel.score_samples(zip(*positions[1])))
    kde2 = np.reshape(k_pos2.T, xy[1][0].shape)
    plt.imshow(np.rot90(kde2), cmap=plt.cm.YlOrBr, extent=bbox)
    plt.contour(xy[1][0],  xy[1][1], kde2, 5, colors='k', linewidths=0.6)

    plt.subplot(gs[2])
    title = 'Roads KDE\nbw: ' + str(bandwidth) + ' 500m'
    plt.title(title, x=0.5, y=0.92, fontsize=12)
    k_pos3 = np.exp(kernel.score_samples(zip(*positions[2])))
    kde3 = np.reshape(k_pos3.T, xy[2][0].shape)
    plt.imshow(np.rot90(kde3), cmap=plt.cm.YlOrBr, extent=bbox)
    plt.contour(xy[2][0], xy[2][1], kde3, 5, colors='k', linewidths=0.6)

    fig.tight_layout()
    plt.show()
