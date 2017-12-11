#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create list of all unique locations (and their keys).
"""

import numpy as np
import pandas as pd

db = pd.read_csv("database.csv")
loc_key_to_name = dict(zip(db.location1Key.values, db.location1Name.values))
loc_key_to_name.update(dict(zip(db.location2Key.values, db.location2Name.values)))

keys = loc_key_to_name.keys()
names = loc_key_to_name.values()

locations = pd.DataFrame.from_dict(dict(locationKey=keys, locationName=names))
locations.to_csv("permanent_locations.csv", columns=['locationKey', 'locationName'])
