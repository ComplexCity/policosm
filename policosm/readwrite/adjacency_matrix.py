"""Read and write graphs in adjacency matrix format.

Adjacency matrix saves a graph as
    1 - a list of vertices of size n
    2 - a matrix of vertices x vertices of size n^2

The matrix is symmetrical if for an undirected graph.

This implementation does not support mixed graphs (directed and
undirected edges together).

Format
------
adjacency matrix is made into two CSV. vertices.csv and edges.csv
"""

import geopandas as gpd


def read_ajdm(vertices_filepath: str, edges_filepath: str, epsg: int) -> gpd.GeoDataFrame:
    # TODO write the reading function
    return None


def write_adjm(gdf: gpd.GeoDataFrame, vertices_filepath: str, edges_filepath: str, epsg: int) -> None:
    """Write adjacency matrix from geopandas to path.
    Adjacency matrix is a square matrix of |vertices| x |vertices| indicating edges as an integer.
    Parameters
    ----------
    gdf : geodataframe
        A geopandas dataframe
    vertices_filepath : file or string
       File or file name to write.
       File names ending in .gz or .bz2 will be compressed.
    edges_filepath : string (optional, default: 'utf-8')
       Encoding for text data.
    Examples
    --------
    >>>
    Notes
    -----
    This implementation does not support mixed graphs (directed and undirected
    edges together).
    The node id attribute is set to be the string of the node label.
    If you want to specify an id use set it as node data, e.g.
    node['a']['id']=1 to set the id of node 'a' to 1.
    References
    ----------
    .. [1] GEXF File Format, https://gephi.org/gexf/format/
    .. [2] GEXF viz schema 1.1, https://gephi.org/gexf/1.1draft/viz
    """
    pass
