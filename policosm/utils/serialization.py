#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in March 2020 in UTSEUS, Shanghai University

@author: github.com/fpfaende

what it does
    serialize, unserialize dataframes
"""

import geopandas as gpd
import geoparquet as gpq
import pandas as pd


def geodataframe_to_pickle(gdf:gpd.GeoDataFrame, filename:str) -> None:
    gdf.to_pickle(filename)


def geodataframe_read_pickle(filename:str, projection: int) -> gpd.GeoDataFrame:
    df = pd.read_pickle(filename)
    gdf= gpd.GeoDataFrame(df, geometry='geometry')
    gdf.crs = "EPSG:{0}".format(projection)
    return gdf


def geodataframe_to_geoparquet(gdf:gpd.GeoDataFrame, filename:str) -> None:
    gdf.to_geoparquet(filename)


def geodataframe_read_geoparquet(filename:str) -> gpd.GeoDataFrame:
    return gpq.read_geoparquet(filename)


