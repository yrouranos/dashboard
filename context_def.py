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


class Context:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object context.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Constructor.
    def __init__(self):

        # View (selected and all).
        self.view = None
        self.views = None

        # Plotting library (selected and all).
        self.lib = None
        self.libs = None

        # Variable or index (selected and all).
        self.varidx = None
        self.varidxs = None

        # Horizons (selected and all).
        self.hor = None
        self.hors = None

        # Emission scenarios (selected and all).
        self.rcp = None
        self.rcps = None

        # Statistics (selected and all).
        self.stat = None
        self.stats = None

        # Platform.
        self.platform = ""

        # Anomalies.
        self.delta = False