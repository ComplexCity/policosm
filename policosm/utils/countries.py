#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created in June 2016 in ComplexCity Lab

@author: github.com/fpfaende

what it does
    define integer roads levels according to highway tag in open street map
"""

right_hand_drive_countries = ['aia', 'atg', 'aus', 'bhs', 'bgd', 'brb', 'bmu', 'btn', 'bwa', 'brn', 'cym', 'cxr', 'cck',
                             'cok', 'cyp', 'dma',
                             'tls', 'gbr', 'flk', 'fji', 'glp', 'ggy', 'guy', 'hkg', 'ind', 'idn', 'irl', 'gbr', 'imn',
                             'jam', 'jpn', 'jey',
                             'ken', 'kir', 'lso', 'mwi', 'mys', 'mdv', 'mlt', 'mus', 'msr', 'moz', 'nam', 'nru', 'npl',
                             'nzl', 'niu', 'nfk',
                             'gbr', 'pak', 'png', 'pcn', 'kna', 'lca', 'shn', 'wsm', 'syc', 'sgp', 'slb', 'zaf', 'lka',
                             'sur', 'tza', 'tha',
                             'tkl', 'ton', 'tto', 'tca', 'tuv', 'uga', 'vgb', 'vir', 'zmb', 'zwe']


def is_right_hand_drive(country_iso3):
    return country_iso3 in right_hand_drive_countries
