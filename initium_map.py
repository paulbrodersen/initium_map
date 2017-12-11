#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import numpy as np
import matplotlib.pyplot as plt; plt.ion()
import pandas as pd

from netgraph._interactive_variants import InteractiveGrid, InteractiveHypergraph

class InteractiveGridHypergraph(InteractiveHypergraph, InteractiveGrid):
    """
    Combination of InteractiveGrid and InteractiveHyperGraph.
    """
    pass


if __name__ == '__main__':

    permanent_paths = pd.read_csv("permanent_paths.csv")

    edge_list   = permanent_paths[['location1Key', 'location2Key']].values.tolist()
    sources     = permanent_paths[['location1Key', 'location1Name']].values.tolist()
    targets     = permanent_paths[['location2Key', 'location2Name']].values.tolist()

    # convert list of lists to list of tuples to make them hashable
    edge_list = [tuple(item) for item in edge_list]
    sources   = [tuple(item) for item in sources]
    targets   = [tuple(item) for item in targets]

    node_labels = dict(sources+targets)
    edge_labels = permanent_paths['pathKey'].values.tolist()
    edge_labels = dict(zip(edge_list, edge_labels))

    permanent_locations = pd.read_csv("permanent_locations.csv")
    node_positions = permanent_locations[['locationKey', 'position']].values.tolist()
    node_positions = {k : v for k, v in node_positions if not np.isnan(v)}

    # plot
    g = InteractiveGridHypergraph(edge_list, node_positions=node_positions, node_labels=node_labels)
