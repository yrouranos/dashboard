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

import def_object

code_script = "script"
code_jupyter = "jupyter"
code_streamlit = "streamlit"


class Context(def_object.Obj):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object context.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, code):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Context, self).__init__(code, code)

        # Data ---------------------------------

        # Project.
        self.project = None
        self.projects = None

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

        # Models (selected and all).
        self.model = None
        self.models = None

        # Deltas.
        self.delta = None
        self.deltas = None

        # File system --------------------------

        # Geospatial files (maps).
        self.p_locations = ""
        self.p_bounds = ""

        # Map ----------------------------------

        # Resolution.
        self.dpi = 600

        # Background color of sidebar.
        self.col_sb_fill = "WhiteSmoke"

        """
        Color maps apply to categories of variables and indices.
        +----------------------------+------------+------------+
        | Variable, category         |   Variable |      Index |
        +----------------------------+------------+------------+
        | temperature, high values   | temp_var_1 | temp_idx_1 |
        | temperature, low values    |          - | temp_idx_2 |
        | precipitation, high values | prec_var_1 | prec_idx_1 |
        | precipitation, low values  |          - | prec_idx_2 |
        | precipitation, dates       |          - | prec_idx_3 |
        | wind                       | wind_var_1 | wind_idx_1 |
        +----------------------------+------------+------------+
        
        Notes:
        - The 1st scheme is for absolute values.
        - The 2nd scheme is divergent and his made to represent delta values when both negative and positive values are
          present.
          It combines the 3rd and 4th schemes.
        - The 3rd scheme is for negative-only delta values.
        - The 4th scheme is for positive-only delta values.
        """

        self.opt_map_col_temp_var   = ["viridis",   "RdBu_r",  "Blues_r",   "Reds"]  # Temperature variables.
        self.opt_map_col_temp_idx_1 = self.opt_map_col_temp_var                      # Temperature indices (high).
        self.opt_map_col_temp_idx_2 = ["plasma_r",    "RdBu",   "Reds_r",  "Blues"]  # Temperature indices (low).
        self.opt_map_col_prec_var   = ["Blues",     "BrWhGr", "Browns_r", "Greens"]  # Precipitation variables.
        self.opt_map_col_prec_idx_1 = self.opt_map_col_prec_var                      # Precipitation indices (high).
        self.opt_map_col_prec_idx_2 = ["Oranges", "BrWhGr_r", "Greens_r", "Browns"]  # Precipitation indices (low).
        self.opt_map_col_prec_idx_3 = ["viridis",   "RdBu_r",  "Blues_r",   "Reds"]  # Precipitation indices (other).
        self.opt_map_col_wind_var   = ["None",      "RdBu_r",  "Blues_r",   "Reds"]  # Wind variables.
        self.opt_map_col_wind_idx_1 = ["Reds",      "RdBu_r",  "Blues_r",   "Reds"]  # Wind indices.
        self.opt_map_col_default    = ["viridis",   "RdBu_r",  "Blues_r",   "Reds"]  # Other variables and indices.

        # Discrete vs. continuous colors scales (maps).
        self.opt_map_discrete = True
