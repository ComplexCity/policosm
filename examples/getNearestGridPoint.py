import csv
import math
import os

##############################################################################################
# To get the nearest point to the defined city center on the grids (100, 250, 500)
##############################################################################################

_CITY = "Vernon"

# City centers we found by looking at a map
_CENTERS = {
    'SaintMalo': [[-2.0255237817764282, 48.648868156113565],
                  [-1.9913524389266968, 48.62354260670266],
                  [-1.9703882932662964, 48.65794028702302]],
    'Pau': [[-0.368267297744751, 43.29436853299735]],
    'Vernon': [[1.4858472347259521, 49.093299578934804],
               [1.4832508563995361, 49.07850155481095]]
}

# Grids, only a csv of longitudes and latitudes of the grid
_GRID_FILES = {
    'SaintMalo': ["data/gridSaintMalo100.csv", "data/gridSaintMalo250.csv", "data/gridSaintMalo500.csv"],
    'Pau': ["data/gridPau100.csv", "data/gridPau250.csv", "data/gridPau500.csv"],
    'Vernon': ["data/gridVernon100.csv", "data/gridVernon250.csv", "data/gridVernon500.csv"]
}

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)

    for rel_path in _GRID_FILES[_CITY]:
        print rel_path
        file_path = os.path.join(script_dir, rel_path)

        with open(file_path, 'r') as fp:
            reader = csv.reader(fp, delimiter=',')

            grid_points = [[float(line[0]), float(line[1])] for line in reader]

            for center in _CENTERS[_CITY]:
                closest_point = min(grid_points,
                                    key=lambda x: math.sqrt(((x[0] - center[0]) ** 2) + ((x[1] - center[1]) ** 2))
                                    )
                print closest_point
