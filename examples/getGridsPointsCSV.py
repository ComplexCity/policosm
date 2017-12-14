# coding=utf-8
import csv
import os
import networkx as nx
from osgeo import ogr, osr
from policosm import simplify, getCentroidsFromRoadsGraph
from policosm.functions.getKernelDensityEstimationForDifferentGrids import getGrid
from getRoadsCentroidsKDE import convertGraphCoord, removeLevelTwoEdges

def convertPointsCoordinates(points, sourceEPSG, targetEPSG):
    sourceProjection = osr.SpatialReference()
    sourceProjection.ImportFromEPSG(sourceEPSG)
    destinationProjection = osr.SpatialReference()
    destinationProjection.ImportFromEPSG(targetEPSG)
    coordTrans = osr.CoordinateTransformation(sourceProjection, destinationProjection)
    new_points = []
    for coord in points:
        x, y = coord
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x,y)
        point.Transform(coordTrans)
        new_points.append((point.GetX(), point.GetY()))
    return new_points


# Grids is a list of grids, one grid being a list of points
def getGridsPointsCSV(grids):
    for idx, grid in enumerate(grids):
        with open('grid' + str(grid_sizes[idx]) + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for coord in grid:
                writer.writerow(coord)


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

    # Convert grids of roads centroids in epsg 4326
    converted_grids = []
    for grid in grids:
        converted_grids.append(convertPointsCoordinates(grid, 3948, 4326))

    getGridsPointsCSV(converted_grids)
