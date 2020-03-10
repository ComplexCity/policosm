"""
This page implements the bicycle wiki page 
https://wiki.openstreetmap.org/wiki/Bicycle#Bicycle_Restrictions

it creates 4 values: forward, backward, safety_forward, safety_backward
forward is in the same direction as the current way
backward is the opposite direction
safety_forward is the safety for the forward way
safety_backward is the safety of the opposite direction

0 - no sidewalk and/or level 4-6 / no sidewalk
1 - sidewalk and/or level 3 / share space / sidewalk
2 - designated but shared / lane marked in the road
3 - designated / lane separated 
"""

from policosm.utils.access import get_access
from policosm.utils.countries import is_right_hand_drive


def get_bicycle(tags, level, country_iso3):
    if is_right_hand_drive(country_iso3):
        return get_right_hand_bicycle(tags, level, country_iso3)
    else:
        return get_left_hand_bicycle(tags, level, country_iso3)


def get_left_hand_bicycle(tags, level, country_iso3):
    sidewalk_use = tags.get('sidewalk:bicycle') == 'yes' or tags.get('sidewalk:left:bicycle') == 'yes' or tags.get(
        'sidewalk:right:bicycle') == 'yes' or tags.get('sidewalk:both:bicycle') == 'yes' or tags.get('sidewalk') in [
                       'both', 'right', 'left', 'yes']

    general = tags.get('highway') == 'cycleway'
    general_oneway = general and tags.get('oneway') == 'yes'

    # ––––––––––––––––– BIDIRECTIONNAL –––––––––––––––––
    # no need to add a new special highway
    # bike is TRUE
    # safety = 2
    rl1a = ('highway' in tags and tags.get('cycleway') == 'lane') or (
            'highway' in tags and tags.get('cycleway:left') == 'lane' and tags.get('cycleway:right') == 'lane') or (
                   tags.get('cycleway:both') == 'lane')

    rl1b = 'highway' in tags and tags.get('cycleway:right') == 'lane' and tags.get('cycleway:right:oneway') in ['false',
                                                                                                                'no',
                                                                                                                'none',
                                                                                                                '0']

    rl2 = 'highway' in tags and tags.get('cycleway:right') == 'lane'

    # ––––––––––––––––– ONE–DIRECTIONNAL LANES–––––––––––––––––
    rm1 = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane' and tags.get(
        'oneway:bicycle') == 'no') or ('highway' in tags and tags.get('oneway') == 'yes' and tags.get(
        'cycleway:left') == 'opposite_lane' and tags.get('cycleway:right') == 'lane')

    rm2a = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway:right') == 'lane') or (
            'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane')

    rm2b = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway:left') == 'lane') or (
            'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane')

    rm2c = 'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane' and tags.get(
        'lanes') == '2'

    rm2d = 'highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no' and tags.get(
        'cycleway:left') == 'lane' and tags.get('cycleway:left:oneway') == 'no'

    rm3a = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no' and tags.get(
        'cycleway:left') == 'opposite_lane') or ('highway' in tags and tags.get('oneway') == 'yes' and tags.get(
        'oneway:bicycle') == 'no' and tags.get('cycleway') == 'opposite_lane')

    rm3b = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no' and tags.get(
        'cycleway:right') == 'opposite_lane') or ('highway' in tags and tags.get('oneway') == 'yes' and tags.get(
        'oneway:bicycle') == 'no' and tags.get('cycleway') == 'opposite_lane')

    # ––––––––––––––––– ONE–DIRECTIONNAL TRACKS–––––––––––––––––
    rt1 = 'highway' in tags and tags.get('cycleway') == 'track'

    rt2 = 'highway' in tags and tags.get('cycleway:right') == 'track' and tags.get('cycleway:right:oneway') == 'no'

    rt3 = 'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway:right') == 'track' and tags.get(
        'oneway:bicycle') == 'no'

    rt4 = 'highway' in tags and tags.get('cycleway:right') == 'track'

    # ––––––––––––––––– SPECIAL –––––––––––––––––
    rs1 = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no') or (
            'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'opposite')

    rs2 = 'highway' in tags and tags.get('cycleway:right') == 'lane' and tags.get('cycleway:left') == 'track'

    rs3 = 'highway' in tags and tags.get('cycleway') == 'track' and tags.get('segregated') == 'yes'

    rs5 = tags.get('highway') == 'path' and tags.get('segregated') == 'yes' and tags.get(
        'foot') == 'designated' and tags.get('bicycle') == 'designated'

    # ––––––––––––––––– CYCLE AND BUS –––––––––––––––––
    if tags.get('bicycle:lanes') is not None:
        rb1 = 'highway' in tags and 'designated' in tags.get('bicycle:lanes').split('|')
    else:
        rb1 = False
    rb3 = 'highway' in tags and tags.get('cycleway:left') == 'lane' and tags.get('cycleway:right') == 'share_busway'

    rb4 = tags.get('highway') == 'service' and tags.get('service') == 'bus' and tags.get(
        'oneway') == 'yes' and tags.get('cycleway:right') == 'share_busway'

    rb5 = 'highway' in tags and tags.get('busway:right') == 'lane' and tags.get('cycleway:right') == 'share_busway'

    rb6 = ('highway' in tags and tags.get('cycleway:left') == 'share_busway' and tags.get(
        'busway') == 'opposite_lane' and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no') or (
                      'highway' in tags and tags.get('cycleway:left') == 'share_busway' and tags.get(
                  'busway') == 'lane' and tags.get('oneway') == 'yes' and tags.get('oneway:bus') == 'no' and tags.get(
                  'oneway:bicycle') == 'no')

    # ––––––––––––––––– MORE SPECIALS –––––––––––––––––
    cyclestreet = 'highway' in tags and tags.get('cyclestreet') == 'yes'
    pedestrians_bicycle = tags.get('highway') == 'pedestrian' and tags.get('bicycle') == 'yes'
    pedestrians = tags.get('highway') == 'pedestrian'
    has_bicycles = tags.get('highway') == 'track' or tags.get('highway') == 'path'
    forbidden = tags.get('bicycle') == 'no'

    if rl1b:
        return True, True, 2, 2
    elif rm1:
        return True, True, 2, 2
    elif rm2a:
        return True, False, 2, -1
    elif rm2c:
        return True, False, 2, -1
    elif rm2d:
        return True, True, 2, 2
    elif rm2b:
        return True, False, 2, -1
    elif rm3a:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 2
    elif rm3b:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 2
    elif rt2:
        return True, True, 3, 3
    elif rt3:
        return True, True, 3, 3
    elif rt4:
        return True, True, 3, 1 if (level <= 3 or sidewalk_use) else 0
    elif rb6:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 2
    elif rs1:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 1
    elif rs2:
        return True, True, 2, 3
    elif rs3:
        return True, True, 3, 3
    elif rt1:
        return True, True, 3, 3
    elif rs5:
        return True, True, 3, 3
    elif rb1:
        return True, True, 2, 2
    elif rb3:
        return True, True, 2, 2
    elif rb4:
        return True, False, 2, -1
    elif rb5:
        return True, True, 2, 1 if (level <= 3 or sidewalk_use) else 0
    elif rl1a:
        return True, True, 2, 2
    elif rl2:
        return True, True, 2, 1 if (level <= 3 or sidewalk_use) else 0
    elif general_oneway:
        return True, False, 3, -1
    elif general:
        return True, True, 3, 3
    elif cyclestreet:
        return True, True, 1, 1
    elif pedestrians_bicycle:
        return True, True, 2, 2
    elif pedestrians:
        return True, True, 1, 1
    elif has_bicycles:
        return True, True, 2, 2
    elif tags.get('oneway') == 'yes':
        if get_access(country_iso3, tags.get('highway'), 'bicycle'):
            return True, False, 1 if (level <= 3 or sidewalk_use) else 0, -1
        else:
            return False, False, -1, -1
    else:
        if get_access(country_iso3, tags.get('highway'), 'bicycle'):
            return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 1 if (level <= 3 or sidewalk_use) else 0
        else:
            return False, False, -1, -1


def get_right_hand_bicycle(tags, level, country_iso3):
    sidewalk_use = tags.get('sidewalk:bicycle') == 'yes' or tags.get('sidewalk:right:bicycle') == 'yes' or tags.get(
        'sidewalk:left:bicycle') == 'yes' or tags.get('sidewalk:both:bicycle') == 'yes' or tags.get('sidewalk') in [
                       'both', 'left', 'right', 'yes']

    general = tags.get('highway') == 'cycleway'
    general_oneway = general and tags.get('oneway') == 'yes'

    # ––––––––––––––––– BIDIRECTIONNAL –––––––––––––––––
    # no need to add a new special highway
    # bike is TRUE
    # safety = 2
    rl1a = ('highway' in tags and tags.get('cycleway') == 'lane') or (
            'highway' in tags and tags.get('cycleway:right') == 'lane' and tags.get('cycleway:left') == 'lane') or (
                   tags.get('cycleway:both') == 'lane')

    rl1b = 'highway' in tags and tags.get('cycleway:left') == 'lane' and tags.get('cycleway:left:oneway') in ['false',
                                                                                                                'no',
                                                                                                                'none',
                                                                                                                '0']

    rl2 = 'highway' in tags and tags.get('cycleway:left') == 'lane'

    # ––––––––––––––––– ONE–DIRECTIONNAL LANES–––––––––––––––––
    rm1 = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane' and tags.get(
        'oneway:bicycle') == 'no') or ('highway' in tags and tags.get('oneway') == 'yes' and tags.get(
        'cycleway:right') == 'opposite_lane' and tags.get('cycleway:left') == 'lane')

    rm2a = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway:left') == 'lane') or (
            'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane')

    rm2b = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway:right') == 'lane') or (
            'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane')

    rm2c = 'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'lane' and tags.get(
        'lanes') == '2'

    rm2d = 'highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no' and tags.get(
        'cycleway:right') == 'lane' and tags.get('cycleway:right:oneway') == 'no'

    rm3a = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no' and tags.get(
        'cycleway:right') == 'opposite_lane') or ('highway' in tags and tags.get('oneway') == 'yes' and tags.get(
        'oneway:bicycle') == 'no' and tags.get('cycleway') == 'opposite_lane')

    rm3b = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no' and tags.get(
        'cycleway:left') == 'opposite_lane') or ('highway' in tags and tags.get('oneway') == 'yes' and tags.get(
        'oneway:bicycle') == 'no' and tags.get('cycleway') == 'opposite_lane')

    # ––––––––––––––––– ONE–DIRECTIONNAL TRACKS–––––––––––––––––
    rt1 = 'highway' in tags and tags.get('cycleway') == 'track'

    rt2 = 'highway' in tags and tags.get('cycleway:left') == 'track' and tags.get('cycleway:left:oneway') == 'no'

    rt3 = 'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway:left') == 'track' and tags.get(
        'oneway:bicycle') == 'no'

    rt4 = 'highway' in tags and tags.get('cycleway:left') == 'track'

    # ––––––––––––––––– SPECIAL –––––––––––––––––
    rs1 = ('highway' in tags and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no') or (
            'highway' in tags and tags.get('oneway') == 'yes' and tags.get('cycleway') == 'opposite')

    rs2 = 'highway' in tags and tags.get('cycleway:left') == 'lane' and tags.get('cycleway:right') == 'track'

    rs3 = 'highway' in tags and tags.get('cycleway') == 'track' and tags.get('segregated') == 'yes'

    rs5 = tags.get('highway') == 'path' and tags.get('segregated') == 'yes' and tags.get(
        'foot') == 'designated' and tags.get('bicycle') == 'designated'

    # ––––––––––––––––– CYCLE AND BUS –––––––––––––––––
    if tags.get('bicycle:lanes') is not None:
        rb1 = 'highway' in tags and 'designated' in tags.get('bicycle:lanes').split('|')
    else:
        rb1 = False
    rb3 = 'highway' in tags and tags.get('cycleway:right') == 'lane' and tags.get('cycleway:left') == 'share_busway'

    rb4 = tags.get('highway') == 'service' and tags.get('service') == 'bus' and tags.get(
        'oneway') == 'yes' and tags.get('cycleway:left') == 'share_busway'

    rb5 = 'highway' in tags and tags.get('busway:left') == 'lane' and tags.get('cycleway:left') == 'share_busway'

    rb6 = ('highway' in tags and tags.get('cycleway:right') == 'share_busway' and tags.get(
        'busway') == 'opposite_lane' and tags.get('oneway') == 'yes' and tags.get('oneway:bicycle') == 'no') or (
                      'highway' in tags and tags.get('cycleway:right') == 'share_busway' and tags.get(
                  'busway') == 'lane' and tags.get('oneway') == 'yes' and tags.get('oneway:bus') == 'no' and tags.get(
                  'oneway:bicycle') == 'no')

    # ––––––––––––––––– MORE SPECIALS –––––––––––––––––
    cyclestreet = 'highway' in tags and tags.get('cyclestreet') == 'yes'
    pedestrians_bicycle = tags.get('highway') == 'pedestrian' and tags.get('bicycle') == 'yes'
    pedestrians = tags.get('highway') == 'pedestrian'
    has_bicycles = tags.get('highway') == 'track' or tags.get('highway') == 'path'
    forbidden = tags.get('bicycle') == 'no'

    if rl1b:
        return True, True, 2, 2
    elif rm1:
        return True, True, 2, 2
    elif rm2a:
        return True, False, 2, -1
    elif rm2c:
        return True, False, 2, -1
    elif rm2d:
        return True, True, 2, 2
    elif rm2b:
        return True, False, 2, -1
    elif rm3a:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 2
    elif rm3b:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 2
    elif rt2:
        return True, True, 3, 3
    elif rt3:
        return True, True, 3, 3
    elif rt4:
        return True, True, 3, 1 if (level <= 3 or sidewalk_use) else 0
    elif rb6:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 2
    elif rs1:
        return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 1
    elif rs2:
        return True, True, 2, 3
    elif rs3:
        return True, True, 3, 3
    elif rt1:
        return True, True, 3, 3
    elif rs5:
        return True, True, 3, 3
    elif rb1:
        return True, True, 2, 2
    elif rb3:
        return True, True, 2, 2
    elif rb4:
        return True, False, 2, -1
    elif rb5:
        return True, True, 2, 1 if (level <= 3 or sidewalk_use) else 0
    elif rl1a:
        return True, True, 2, 2
    elif rl2:
        return True, True, 2, 1 if (level <= 3 or sidewalk_use) else 0
    elif general_oneway:
        return True, False, 3, -1
    elif general:
        return True, True, 3, 3
    elif cyclestreet:
        return True, True, 1, 1
    elif pedestrians_bicycle:
        return True, True, 2, 2
    elif pedestrians:
        return True, True, 1, 1
    elif has_bicycles:
        return True, True, 2, 2
    elif tags.get('oneway') == 'yes':
        if get_access(country_iso3, tags.get('highway'), 'bicycle'):
            return True, False, 1 if (level <= 3 or sidewalk_use) else 0, -1
        else:
            return False, False, -1, -1
    else:
        if get_access(country_iso3, tags.get('highway'), 'bicycle'):
            return True, True, 1 if (level <= 3 or sidewalk_use) else 0, 1 if (level <= 3 or sidewalk_use) else 0
        else:
            return False, False, -1, -1


if __name__ == '__main__':
    tags = {'highway': 'motorway'}
    print(get_bicycle(tags, 8, 'fra'))
    tags = {'name':'Rue d\'Amboise','oneway':'yes','highway':'service','service':'alley','wikidata':'Q3450464','cycleway:left':'opposite','oneway:bicycle':'no'}
    print(get_bicycle(tags, 2, 'fra'))
    tags = {'oneway':'yes','highway':'residential','surface':'asphalt','maxspeed':30,'busway:right':'lane','cycleway:right':'share_busway','oneway:bicycle':'yes'}
    print(get_bicycle(tags, 3, 'fra'))
