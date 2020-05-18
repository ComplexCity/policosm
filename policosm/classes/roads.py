#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in February 2017 in ComplexCity Lab

@author: github.com/fpfaende

what it does
    Roads sets callback functions for ways in osm files targeting roads
    the osm roads are transform into graphs

parameters
    functions are called with callback from osmium
    nodes coordinates parameters are in the following format [[id,lon,lat],[id,lon,lat]]
    edges ways

how it works
    create a series of nodes each time osm parser send nodes
    test a series of rules to create edges each time osm parser send a way
    the node contains latitude and longitude information
    the edge contains ['lanes', 'osmid', 'footway', 'level', 'bicycle', 'oneway', 'highway'] informations

TODO ADD MAX SPEED TO ROADS
TODO -> later add bearing, length, speed, all shortest path, filter per transportation
"""
import logging
import re

import geopandas as gpd
import networkx as nx
import osmium
import pandas as pd
import pint
from shapely.geometry import LineString

from policosm.geoNetworks import simplify_directed_as_dataframe
from policosm.utils.access import get_access
from policosm.utils.bicycles import get_bicycle
from policosm.utils.levels import get_level
from policosm.utils.projections import get_most_accurate_epsg
from policosm.utils.serialization import geodataframe_to_geoparquet

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# init regex for lane width analysis and unit transformation
width_matcher_regex = r"(?P<width>([0-9]+([.,][0-9]*)?|[.][0-9]+)((\s([a-z]+))|([\'\"]))?)"
width_matcher = re.compile(width_matcher_regex)
ureg = pint.UnitRegistry()

# init regex for lane analysis
lanes_matcher_regex = r"(?P<lanes>([0-9]+([.,][0-9]*)?|[.][0-9]+))"
lanes_matcher = re.compile(lanes_matcher_regex)

sidewalk_pattern = re.compile('^sidewalk*')


def get_width_from_tag(width):
    matches = width_matcher.findall(width.replace(',', '.'))
    if len(matches) > 0:
        widths = [(m[0], m[0][-1].strip() == 'm') for m in matches]
        widths.sort(key=lambda x: x[1], reverse=True)
    else:
        return None

    if widths[0][1] is not True:
        fandi = []
        for w in widths:
            if '\'' in w[0]:
                fandi.append(w[0].replace('\'', 'feet'))
            if '\"' in w[0]:
                fandi.append(w[0].replace('\"', 'inches'))
        if len(fandi) > 0:
            return sum([ureg.Quantity(fi).to(ureg.meter).magnitude for fi in fandi])
        else:
            try:
                return ureg.Quantity(widths[0][0]).to(ureg.meter).magnitude
            except pint.registry.DimensionalityError:
                return float(widths[0][0])
    else:
        return ureg.Quantity(widths[0][0]).to(ureg.meter).magnitude


def get_width(tags, lanes, level, country_iso3):
    if 'width' in tags:
        raw_width = tags['width']
        width = get_width_from_tag(raw_width)
        if width is not None and isinstance(width, float) and width > 2.0 * lanes:
            return width

    if country_iso3 == 'usa' and level > 6:
        return 3.7 * lanes
    elif country_iso3 == 'deu' and level > 4:
        return 3.5 * lanes
    elif level < 3:
        return 1.5 * lanes
    else:
        return 3.0 * lanes


def get_one_way(tags, highway):
    # first cleanup one_way
    one_way = tags.get('oneway')
    if one_way == 'yes':
        return True, False, tags
    elif one_way == 'no':
        return False, False, tags
    elif one_way is not None:
        if one_way == 'true' or str(one_way) == '1':
            tags['oneway'] = 'yes'
            return True, False, tags
        elif one_way == 'false' or str(one_way) == '0':
            tags['oneway'] = 'no'
            return False, False, tags
        elif one_way == '-1' or one_way == 'reverse':
            return True, True, tags
        elif one_way == 'reversible' or one_way == 'alternating':
            tags['oneway'] = 'no'
            return False, False, tags

    junction = tags.get('junction')
    if junction is not None:
        if junction == 'circular' or junction == 'roundabout':
            if one_way is None:
                tags['oneway'] = 'yes'
            return True, False, tags

    if highway == 'motorway':
        if one_way is None:
            tags['oneway'] = 'yes'
        return True, False, tags

    return False, False, tags


def get_lanes(tags, level, oneway):
    if 'lanes' in tags:
        lanes = tags['lanes']
        matches = lanes_matcher.findall(lanes)
        try:
            if len(matches) > 0:
                return int(matches[0][0])
        except ValueError:
            logging.error('lanes tag value error for {0} default to 1'.format(tags['lanes']))
    else:
        if 3 <= level <= 6:
            if oneway:
                return 1
            else:
                return 2
        elif level >= 7:
            return 2
        else:
            return 1


def get_foot(tags, highway, level, country_iso3):
    """
    Returns a tuple (foot TRUE|FALSE, safety 0->3)
    safety
    -1 - not allowed
    0 - no sidewalk and/or level 4-6
    1 - sidewalk and/or level 3
    2 - designated but shared
    3 - designated
    """
    foot = False
    safety = 0

    if tags.get('foot') in ['yes', 'true', '1', 'designated'] or tags.get('footway') in ['yes', 'true', '1',
                                                                                         'designated']:
        foot = True
    elif tags.get('pedestrian') in ['yes', 'true', '1']:
        foot = True
    elif tags.get('access') in ['yes', 'true', '1', 'designated', 'permissive', 'unknown']:
        foot = True
    elif get_access(country_iso3, highway, 'foot'):
        foot = True

    if foot is False:
        return foot, -1

    tags_list = [str(i) for i in tags]
    if highway in ['pedestrian', 'path']:
        if tags.get('segregated') == 'yes':
            safety = 3
        elif tags.get('foot') == 'designated':
            safety = 3
        else:
            safety = 2
    elif highway in ['cycleway', 'bicycle']:
        if tags.get('segregated') == 'yes':
            safety = 3
        elif tags.get('foot') == 'designated':
            safety = 3
        else:
            safety = 1
    elif highway == 'track':
        safety = 2

    elif len(list(filter(sidewalk_pattern.match, tags_list))) > 0:
        sidewalk = list(filter(sidewalk_pattern.match, tags_list))[0]
        logging.debug('sidewalk tag is {0}'.format(sidewalk))

        if tags.get(sidewalk) not in ['false', 'no', 'none', '0']:
            safety = 1
    elif highway == 'footway':
        safety = 3
    elif level < 2:
        safety = 2
    elif level < 4:
        safety = 1

    return foot, safety


def get_max_speed(tags):
    """
    :type tags: object
    """
    max_speed = tags.get('maxspeed', -1)
    try:
        max_speed = int(max_speed)
    except ValueError:
        if max_speed == 'walk':
            return 6
        else:
            return -1
    return max_speed


class Roads(osmium.SimpleHandler):
    def __init__(self, directed:bool=False, country_iso3:str='zzz', level_upper_bound:int=8, level_lower_bound:int=2):
        osmium.SimpleHandler.__init__(self)

        self.directed = directed
        if self.directed:
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()

        self.country_iso3 = country_iso3
        self.projection = None

        self.vertices_tuples = []
        self.edges_tuples = []

        self.dfv = None
        self.dfe = None
        self.level_upper_bound = level_upper_bound
        self.level_lower_bound = level_lower_bound

    def node(self, n):
        osm_id = n.id
        lon = n.location.lon
        lat = n.location.lat
        self.vertices_tuples.append((osm_id, lon, lat))

    def way(self, w):
        osm_id = w.id
        tags = w.tags

        attributes = dict()
        tags = {tag.k: tag.v for tag in w.tags}

        # 1 GENERAL highway
        if 'highway' not in tags:
            if 'foot' not in tags:
                if 'bicycle' not in tags:
                    if 'pedestrian' not in tags:
                        return
                    else:
                        if tags['pedestrian'] in ['yes', 'true', '1']:
                            attributes['highway'] = 'footway'
                            tags['highway'] = attributes['highway']
                        else:
                            return
                else:
                    if tags['bicycle'] in ['yes', 'true', '1'] or tags['bicycle'] == 'designated':
                        attributes['highway'] = 'cycleway'
                        tags['highway'] = attributes['highway']
                    else:
                        return
            else:
                if tags['foot'] in ['yes', 'true', '1']:
                    attributes['highway'] = 'pedestrian'
                    tags['highway'] = attributes['highway']
                else:
                    return
        else:
            attributes['highway'] = tags['highway']

        # 2 GENERAL level according to highway
        attributes['level'] = get_level(attributes['highway'])
        if attributes['level'] > self.level_upper_bound or attributes['level'] < self.level_lower_bound:
            return

        # 3 GENERAL oneway (oneway, reverse)
        attributes['oneway'], attributes['reversed'], tags = get_one_way(tags, attributes['highway'])

        # 4 GENERAL lanes according to level
        attributes['lanes'] = get_lanes(tags, attributes['level'], attributes['oneway'])

        # 5 GENERAL width according to lanes
        attributes['width'] = get_width(tags, attributes['lanes'], attributes['level'], self.country_iso3)

        # 6 SPECIFIC bicycle with rules
        attributes['bicycle_forward'], attributes['bicycle_backward'], attributes['bicycle_safety_forward'], attributes[
            'bicycle_safety_backward'] = get_bicycle(tags, attributes['level'], self.country_iso3)
        # use bicycle lane to create an alternate 

        # 7 SPECIFIC footway with rules
        attributes['foot'], attributes['foot_safety'] = get_foot(tags, attributes['highway'], attributes['level'],
                                                                 self.country_iso3)
        # 8 SPECIFIC motorcar with rules maxspeed
        attributes['maxspeed'] = get_max_speed(tags)
        attributes['motorcar'] = get_access(self.country_iso3, attributes['highway'], 'motorcar')

        us = [i.ref for i in w.nodes][:-1]
        vs = [i.ref for i in w.nodes][1:]

        for i, (u, v) in enumerate(zip(us, vs)):
            osm_id_prefix = '{0}-{1}'.format(osm_id, i)
            if self.directed is False:
                self.edges_tuples.append(
                    (osm_id_prefix, u, v, attributes['highway'], attributes['oneway'], attributes['level'],
                     attributes['lanes'], attributes['width'], attributes['bicycle_forward'],
                     attributes['bicycle_safety_forward'],
                     attributes['foot'], attributes['foot_safety'], attributes['maxspeed'], attributes['motorcar']))
            else:
                if attributes['oneway'] is False:
                    # add forward edge
                    self.edges_tuples.append(
                        (osm_id_prefix, u, v, attributes['highway'], attributes['oneway'], attributes['level'],
                         attributes['lanes'], attributes['width'], attributes['bicycle_forward'],
                         attributes['bicycle_safety_forward'],
                         attributes['foot'], attributes['foot_safety'], attributes['maxspeed'], attributes['motorcar']))
                    # add backward edge
                    self.edges_tuples.append(
                        (osm_id_prefix + '-r', v, u, attributes['highway'], attributes['oneway'], attributes['level'],
                         attributes['lanes'], attributes['width'], attributes['bicycle_backward'],
                         attributes['bicycle_safety_backward'],
                         attributes['foot'], attributes['foot_safety'], attributes['maxspeed'], attributes['motorcar']))
                else:
                    # if we have to add only one direction BUT bike is authorize in the other way... or Foot...
                    # depending on the country and the access, we add a reverse footway...
                    if attributes['reversed'] is True:
                        self.edges_tuples.append(
                            (osm_id_prefix + '-1', v, u, attributes['highway'], attributes['oneway'],
                             attributes['level'],
                             attributes['lanes'], attributes['width'], attributes['bicycle_backward'],
                             attributes['bicycle_safety_backward'],
                             attributes['foot'], attributes['foot_safety'], attributes['maxspeed'],
                             attributes['motorcar']))
                        if attributes['bicycle_forward']:
                            self.edges_tuples.append(
                                (osm_id_prefix + '-b', u, v, 'cycleway', attributes['oneway'], get_level('cycleway'),
                                 1, 1.5, attributes['bicycle_forward'],
                                 attributes['bicycle_safety_forward'],
                                 False, 0, 30, False))
                        if attributes['foot']:
                            self.edges_tuples.append(
                                (osm_id_prefix + '-f', u, v, 'footway', attributes['oneway'], get_level('footway'),
                                 1, 1.5, False,
                                 -1,
                                 True, 1, 30, False))
                    else:
                        self.edges_tuples.append(
                            (osm_id_prefix, u, v, attributes['highway'], attributes['oneway'], attributes['level'],
                             attributes['lanes'], attributes['width'], attributes['bicycle_forward'],
                             attributes['bicycle_safety_forward'],
                             attributes['foot'], attributes['foot_safety'],
                             attributes['maxspeed'], attributes['motorcar']))
                        if attributes['bicycle_backward']:
                            self.edges_tuples.append(
                                (osm_id_prefix + '-1b', v, u, 'cycleway', attributes['oneway'], get_level('cycleway'),
                                 1, 1.5, attributes['bicycle_backward'],
                                 attributes['bicycle_safety_backward'],
                                 False, 0, 30, False))
                        if attributes['foot']:
                            self.edges_tuples.append(
                                (osm_id_prefix + '-1f', v, u, 'footway', attributes['oneway'], get_level('footway'),
                                 1, 1.5, False,
                                 -1,
                                 True, 1, 30, False))

    def osm_to_dataframes(self, project_to_meters=True):
        logging.info('convert osm vertices tuple to dataframe')
        # create the dataframe from tuples
        df = pd.DataFrame.from_records(self.vertices_tuples, index='osm_id',
                                       columns=['osm_id', 'longitude', 'latitude'])
        df[['longitude', 'latitude']] = df[['longitude', 'latitude']].astype(float)
        dfv = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
        dfv.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
        self.projection = 4326

        if project_to_meters:
            sample_coordinates = tuple(dfv[['longitude', 'latitude']].sample(n=1).to_numpy()[0])
            self.projection = get_most_accurate_epsg(sample_coordinates)
            logging.debug(
                'projection for {}, {}: {}'.format(sample_coordinates[0], sample_coordinates[1], self.projection))
            dfv.to_crs(epsg=self.projection, inplace=True)

        geoms = dict(zip(dfv.index.to_list(), dfv['geometry'].to_list()))

        logging.info('convert osm edges tuple to dataframe')
        dfe = pd.DataFrame.from_records(self.edges_tuples, index='osm_id',
                                             columns=['osm_id', 'u', 'v', 'highway', 'one_way', 'level', 'lanes',
                                                      'width', 'bicycle', 'bicycle_safety',
                                                      'foot', 'foot_safety', 'max_speed', 'motorcar'])
        dfe['source'] = dfe.u.apply(geoms.get)
        dfe['target'] = dfe.v.apply(geoms.get)
        dfe['line'] = dfe.apply(lambda e: [e.source, e.target], axis=1)
        dfe.dropna(inplace=True)
        dfe['geometry'] = dfe.line.apply(LineString)
        dfe.drop(columns=['source', 'target', 'line'], inplace=True)
        self.dfe = gpd.GeoDataFrame(dfe, geometry='geometry')
        self.dfe.crs = "EPSG:{0}".format(self.projection)

    def processing_simplify(self):
        """
        ATTENTION dataframe edge becomes geodataframe
        """
        logging.info('Simplify edges dataframe {}'.format(None if len(self.dfe) < 100000 else '(it can take a few hours for a large extract such a this one)'))
        self.dfe = simplify_directed_as_dataframe(self.dfe)

        logging.info('transform path into linestring')
        geoms = dict(zip(self.dfv.index.to_list(), self.dfv['geometry'].to_list()))
        self.dfe['line'] = self.dfe.path.apply(lambda p: [geoms.get(x) for x in p])

        logging.debug('dataframe array of point into linestring')
        self.dfe['geometry'] = self.dfe.line.apply(LineString)
        self.dfe.drop(columns=['path', 'line'], inplace=True)
        self.dfe = gpd.GeoDataFrame(self.dfe, geometry='geometry')
        self.dfe.crs = "EPSG:{0}".format(self.projection)

    def motocar_ways_only(self) -> gpd.GeoDataFrame:
        """
        :return: edges geodataframe where motocar are allowed
        """
        return self.dfe.loc[self.dfe.motocar == 1]

    def bicycle_ways_only(self) -> gpd.GeoDataFrame:
        """
        :return: edges geodataframe where bicycle are allowed
        """
        return self.dfe.loc[self.dfe.bicycle == 1]

    def foot_ways_only(self) -> gpd.GeoDataFrame:
        """
        :return: edges geodataframe where bicycle are allowed
        """
        return self.dfe.loc[self.dfe.foot == 1]


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Start processing')
    roads = Roads(directed=True, country_iso3='fra')
    roads.apply_file('../tests/01249.pbf', locations=True)
    roads.osm_to_dataframes()
    print(roads.dfe.head(n=2))
    #roads.projection = 3949
    #roads.dfe = geodataframe_read_geoparquet('/Users/fabien/Dropbox/Urban Data Hackathon/France-city-network/Paris-Directed-network/ile-cite-directed-edges.geoparquet')# roads.osm_to_dataframes()
    #roads.dfv = geodataframe_read_pickle('paris-vertices.pkl',roads.projection)

    logging.info('dataframe info - {}'.format(roads.dfe.info()))
    roads.dfe = simplify_directed_as_dataframe(roads.dfe)
    logging.info('dataframe info - {}'.format(roads.dfe.info()))
    geodataframe_to_geoparquet(roads.dfe, '/Users/fabien/Dropbox/Urban Data Hackathon/France-city-network/Paris-Directed-network/01249.geoparquet')
