# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Configuration.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import math

# Background color of sidebar.
col_sb_fill = "WhiteSmoke"

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
- The 2nd scheme is divergent and his made to represent delta values when both negative and positive values are present.
  It combines the 3rd and 4th schemes.
- The 3rd scheme is for negative-only delta values.
- The 4th scheme is for positive-only delta values.
"""

# Temperature variables.
opt_map_col_temp_var   = ["viridis", "RdBu_r", "Blues_r", "Reds"]

# Temperature indices (high).
opt_map_col_temp_idx_1 = opt_map_col_temp_var

# Temperature indices (low).
opt_map_col_temp_idx_2 = ["plasma_r", "RdBu", "Reds_r", "Blues"]

# Precipitation variables.
opt_map_col_prec_var   = ["Blues", "BrWhGr", "Browns_r", "Greens"]

# Precipitation indices (high).
opt_map_col_prec_idx_1 = opt_map_col_prec_var

# Precipitation indices (low).
opt_map_col_prec_idx_2 = ["Oranges", "BrWhGr_r", "Greens_r", "Browns"]

# Precipitation indices (other).
opt_map_col_prec_idx_3 = ["viridis", "RdBu_r", "Blues_r", "Reds"]

# Wind variables.
opt_map_col_wind_var   = ["None", "RdBu_r", "Blues_r", "Reds"]

# Wind indices.
opt_map_col_wind_idx_1 = ["Reds", "RdBu_r", "Blues_r", "Reds"]

# Other variables and indices.
opt_map_col_default    = ["viridis", "RdBu_r", "Blues_r", "Reds"]

# Discrete vs. continuous colors scales (maps).
opt_map_discrete = True

# Resolution of figures.
dpi = 600
