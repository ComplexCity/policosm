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
import logging

import geopandas as gpd
import graph_tool.all as gt
import numpy as np
from scipy.sparse import csr_matrix


def adjacency(gdf: gpd.GeoDataFrame, directed: bool=False, weight: str=None, include_vertices_position: bool=False) -> (csr_matrix, list):
    """create weighted adjacency matrix from graph.
    Adjacency matrix is a square matrix of |vertices| x |vertices| indicating edges as an integer.

    Parameters
    ----------
    gdf : :class:`~geopandas.GeoDataFrame`
        A geopandas dataframe with the list of edges
    directed : bool (default to False)
        is the graph directed
    weight :  string (default to None)
       column of the geodataframe to use as a weight
    include_vertices_position :boolean (default to False)
        also return a dictionary of attributes for the vertices ({v:(x,y)}
    Returns
    -------
    adj : :class:`~scipy.sparse.csr_matrix`

    """
    g = gt.Graph(directed=directed)

    if weight is not None:
        if weight not in gdf.columns:
            logging.error('{0} is not in geodataframe columns {1}'.format(weight,gdf.columns))
            return None, None

        data_type_obj = gdf.dtypes[weight]
        if data_type_obj == np.int:
            weight_prop = g.new_edge_property('int')
        else:
            weight_prop = g.new_edge_property('float')

        edgelist = gdf.reset_index()[['u','v',weight]].values
        nodes_id = g.add_edge_list(edgelist, hashed=True, eprops=[weight,])
    else:
        edgelist = gdf.reset_index()[['u','v']].values
        nodes_id = g.add_edge_list(edgelist, hashed=True)

    if not include_vertices_position:
        return gt.adjacency(g,weight_prop), None
    if

def write_adjm(gdf: gpd.GeoDataFrame, vertices_filepath: str, edges_filepath: str) -> None:
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
