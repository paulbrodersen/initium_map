#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clean raw data files provided by ID.
Assemble together with google doc sheet of missing location keys the
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

# --------------------------------------------------------------------------------
# load locations and paths

path_df = pd.read_csv("permanent_paths_raw.csv")
loc_df = pd.read_csv("permanent_locations_raw.csv")
missing_df = pd.read_csv("missing_location_names.csv")

# --------------------------------------------------------------------------------
# remove paths that lead nowhere (null)

remove = np.logical_or(path_df["location1Key"] == "null", path_df["location2Key"] == "null")
path_df = path_df.loc[~remove]

# --------------------------------------------------------------------------------
# create network and restrict to giant connected component (gcc)

g = nx.from_pandas_dataframe(path_df, "location1Key", "location2Key", "KEY")
# g.size()
# 1277
gcc = max(nx.connected_component_subgraphs(g), key=len)
# gcc.size()
# 803

# --------------------------------------------------------------------------------
# create db

# lookup table: key -> name
path_key_to_name = dict(zip(path_df.KEY.values, path_df.name.values))
loc_key_to_name = dict(zip(loc_df.KEY.values, loc_df.name.values))
loc_key_to_name.update(dict(zip(missing_df.missingKey.values, missing_df.missingName.values)))

columns = ['pathKey', 'pathName', 'location1Key', 'location1Name', 'location2Key', 'location2Name']
db = dict()
for col in columns:
    db[col] = list()

for (source_key, target_key, attr) in gcc.edges(data=True):
    path_key, = attr.values()
    db['pathKey'] += [path_key]
    db['pathName'] += [path_key_to_name[path_key]]
    db['location1Key'] += [source_key]
    db['location2Key'] += [target_key]
    try:
        db['location1Name'] += [loc_key_to_name[source_key]]
    except KeyError:
        db['location1Name'] += ['UNKNOWN']
        import warnings; warnings.warn("Cannot find name for location {}".format(source_key))
    try:
        db['location2Name'] += [loc_key_to_name[target_key]]
    except KeyError:
        db['location2Name'] += ['UNKNOWN']
        import warnings; warnings.warn("Cannot find name for location {}".format(target_key))

db_df = pd.DataFrame.from_dict(db)
db_df.to_csv("permanent_paths.csv", columns=columns)
