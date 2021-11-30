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

"""
File system ------------------------------------------------------------------------------------------------------------
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
q_low = str(math.ceil(q_l[0] * 100))
q_high = str(math.ceil(q_l[1] * 100))

"""
Design -----------------------------------------------------------------------------------------------------------------
"""

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

# Plotting libraries (only for time series).
libs = ["altair", "hvplot", "matplotlib"]

# Discrete vs. continuous colors scales (maps).
opt_map_discrete = True
