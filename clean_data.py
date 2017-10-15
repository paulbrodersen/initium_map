#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clean raw data files provided by ID.
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

# --------------------------------------------------------------------------------
# load locations and paths

loc_df = pd.read_csv("permanent_locations_raw.csv")
path_df = pd.read_csv("permanent_paths_raw.csv")

# --------------------------------------------------------------------------------
# remove paths that lead nowhere (null)

remove = np.logical_or(path_df["location1Key"] == "null", path_df["location2Key"] == "null")
path_df = path_df.loc[~remove]

# --------------------------------------------------------------------------------
# create network and restrict to giant component

g = nx.from_pandas_dataframe(path_df, "locations1Key", "location2Key", "KEY")
# g.size()
# 1277
gcc = max(nx.connected_component_subgraphs(g), key=len)
# gcc.size()
# 803

# --------------------------------------------------------------------------------
# save out paths and locations of giant component

# lookup table: key -> name
key_to_name = dict(zip(loc_df.KEY.values, loc_df.name.values))
path_key_to_name = dict(zip(path_df.KEY.values, path_df.name.values))

# make path data frame
source_keys = [source_key for (source_key, target_key, attr) in gcc.edges(data=True)]
target_keys = [target_key for (source_key, target_key, attr) in gcc.edges(data=True)]
path_keys = [attr["KEY"] for (source_key, target_key, attr) in gcc.edges(data=True)]

problems = []

for ii, key in enumerate(source_keys):
    try:
        name = key_to_name[key]
    except:
        print path_keys[ii], path_key_to_name[path_keys[ii]]

for ii, key in enumerate(target_keys):
    try:
        name = key_to_name[key]
    except:
        print path_keys[ii], path_key_to_name[path_keys[ii]]

source_names = [key_to_name[key] for key in source_keys]
target_names = [key_to_name[key] for key in target_keys]

gcc_path_dict = dict()
gcc_path_dict["path key"] = path_keys
gcc_path_dict["source key"] = source_keys
gcc_path_dict["source name"] = source_names
gcc_path_dict["target key"] = target_keys
gcc_path_dict["target name"] = target_names

gcc_path_df = pd.DataFrame.from_dict(gcc_path_dict)

# make location data frame
location_keys = set(source_keys) & set(target_keys)
location_names = [key_to_name[key] for key in location_keys]

gcc_loc_dict = dict()
gcc_loc_dict["name"] = location_names
gcc_loc_dict["key"] = location_keys

gcc_loc_df = pd.DataFrame.from_dict(gcc_loc_dict)

# save out
gcc_path_df.to_csv("permanent_paths_gcc.csv")
gcc_loc_df.to_csv("permanent_locations_gcc.csv")
