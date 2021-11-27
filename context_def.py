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

import hor_def
import lib_def
import rcp_def
import varidx_def as vi
import view_def


class Context:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object context.
    --------------------------------------------------------------------------------------------------------------------
    """

    # View (selected and all).
    view = view_def.View("")
    views = view_def.Views()
    
    # Plotting library (selected and all).
    lib = lib_def.Lib("")
    libs = lib_def.Libs()
    
    # Variable or index (selected and all).
    varidx = vi.VarIdx("")
    varidxs = vi.VarIdxs()
    
    # Horizons (selected and all).
    hor = hor_def.Hor("")
    hors = hor_def.Hors()
    
    # Emission scenarios (selected and all).
    rcp = rcp_def.RCP("")
    rcps = rcp_def.RCPs()
    
    # Constructor.
    def __init__(self):    
        pass
    