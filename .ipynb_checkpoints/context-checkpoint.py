# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Context.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import ghg_scen


class Context:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining a context.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Base directory of data.
    d_data = "./data/"

    # Directory of data related to time series.
    d_ts = d_data + "ts/"

    # Directory of data related to tables of statistics.
    d_tbl = d_data + "tbl/"

    # Directory of data related to maps.
    d_map = d_data + "map/"

    # Path to company logo.
    p_logo = d_data + "ouranos_transparent.png"

    # Region oundaries.
    p_bounds = d_map + "sn_boundaries.geojson"

    # Quantiles.
    q_l = [0.1, 0.9]

    # List of RCP instances.
    rcps = ghg_scen.RCPs()
    
    # Constructor.
    def __init__(self):    
        pass
    