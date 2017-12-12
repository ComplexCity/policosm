# coding=utf-8
import csv
import os
import networkx as nx
from policosm import simplify, getCentroidsFromRoadsGraph
from policosm.functions.getKernelDensityEstimationForDifferentGrids import getGrid
from getRoadsCentroidsKDE import convertGraphCoord, removeLevelTwoEdges


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    rel_path = "data/Saint-Malo.gexf"
    file_path = os.path.join(script_dir, rel_path)

    graph = nx.read_gexf(path=file_path)
    graph = simplify(graph)
    graph = convertGraphCoord(graph)
    graph = removeLevelTwoEdges(graph)
    roads_centroids = getCentroidsFromRoadsGraph(graph)

    grid_sizes = [100, 250, 500]
    grids = getGrid(roads_centroids, grid_sizes)

    for idx, grid in enumerate(grids):
        with open('grid' + str(grid_sizes[idx]) + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for coord in grid:
                writer.writerow(coord)
