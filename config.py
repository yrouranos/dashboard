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

import utils


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
    
"""
Views ------------------------------------------------------------------------------------------------------------------
"""

# Views.
views = {"ts": "Série temporelle", "tbl": "Tableau", "map": "Carte"}

"""
Climate variables (CORDEX) ---------------------------------------------------------------------------------------------
"""

# Temperature (daily mean).
var_cordex_tas = "tas"

# Temperature (daily minimum).
var_cordex_tasmin = "tasmin"

# Temperature (daily maximum).
var_cordex_tasmax = "tasmax"

# Precipitation.
var_cordex_pr = "pr"

# Wind speed, eastward.
var_cordex_uas = "uas"

# Wind speed, northward.
var_cordex_vas = "vas"

# Wind speed (daily maximum).
var_cordex_sfcwindmax = "sfcWindmax"

# Barometric pressure.
var_cordex_ps = "ps"

# Solar radiation.
var_cordex_rsds = "rsds"

# Evaporation.
var_cordex_evspsbl = "evspsbl"

# Potential evapotranspiration.
var_cordex_evspsblpot = "evspsblpot"

# Specific humidity.
var_cordex_huss = "huss"

# Cloud cover.
var_cordex_clt = "clt"

# All variables.
variables_cordex = [var_cordex_tas, var_cordex_tasmin, var_cordex_tasmax,
                    var_cordex_pr, var_cordex_uas, var_cordex_vas, var_cordex_sfcwindmax,
                    var_cordex_ps, var_cordex_rsds, var_cordex_evspsbl,
                    var_cordex_evspsblpot, var_cordex_huss, var_cordex_clt]

"""
Climate indices --------------------------------------------------------------------------------------------------------
"""

# Extreme temperature range.
idx_etr = "etr"

# Number of days with extreme maximum temperature (> 90th percentile).
idx_tx90p = "tx90p"

# Maximum heat wave length.
idx_heat_wave_max_length = "heat_wave_max_length"

# Total heat wave length.
idx_heat_wave_total_length = "heat_wave_total_len"

# Number of hot spells.
idx_hot_spell_frequency = "hot_spell_frequency"

# Maximum hot spell length
idx_hot_spell_max_length = "hot_spell_max_length"

# Mean of mean temperature.
idx_tgg = "tgg"

# Mean of minimum temperature
idx_tng = "tng"

# Maximum of minimum temperature.
idx_tnx = "tnx"

# Mean of maximum temperature
idx_txg = "txg"

# Maximum of maximum temperature
idx_txx = "txx"

# Number of months per year with a mean minimum temperature below a threshold.
idx_tng_months_below = "tng_months_below"

# Number of days per year with maximum temperature above a threshold.
idx_tx_days_above = "tx_days_above"

# Number of days per year with a minimum temperature below a threshold.
idx_tn_days_below = "tn_days_below"

# Number of tropical nights, i.e. with minimum temperature above a threshold
idx_tropical_nights = "tropical_nights"

# Warm spell duration index.
idx_wsdi = "wsdi"

# Largest 1-day precipitation amount.
idx_rx1day = "rx1day"

# Largest 5-day precipitation amount.
idx_rx5day = "rx5day"

# Maximum number of consecutive dry days.
idx_cdd = "cdd"

# Maximum number of consecutive wet days.
idx_cwd = "cwd"

# Number of dry days
idx_dry_days = "dry_days"

# Number of wet days.
idx_wet_days = "wet_days"

# Accumulated total precipitation.
idx_prcptot = "prcptot"

# Number of days with precipitation greater than or equal to 10 mm.
idx_r10mm = "r10mm"

# Number of days with precipitation greater than or equal to 20 mm.
idx_r20mm = "r20mm"

# Number of days with precipitation greater than or equal to a user-provided value.
idx_rnnmm = "rnnmm"

# Mean daily precipitation intensity.
idx_sdii = "sdii"

# Day of year where rain season starts.
idx_rain_season_start = "rain_season_start"

# Day of year where rain season ends.
idx_rain_season_end = "rain_season_end"

# Duration of the rain season.
idx_rain_season_length = "rain_season_length"

# Quantity received during rain season.
idx_rain_season_prcptot = "rain_season_prcptot"

# Total length of dry period.
idx_dry_spell_total_length = "dry_spell_total_length"

# Number of days per year with mean wind speed above a threshold value coming from a given direction.
idx_wg_days_above = "wg_days_above"

# Number of days per year with maximum wind speed above a threshold value.
idx_wx_days_above = "wx_days_above"

# Drought code.
idx_drought_code = "drought_code"

# Rain season (group).
idx_rain_season = "rain_season"
idx_groups = [[idx_rain_season,
              [idx_rain_season_start, idx_rain_season_end, idx_rain_season_length, idx_rain_season_prcptot]]]

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

"""
Instances --------------------------------------------------------------------------------------------------------------
"""