# Emission scenarios.
rcp_ref = "ref"         # Reference period.
rcp_26  = "rcp26"       # Future period RCP 2.6.
rcp_45  = "rcp45"       # Future period RCP 4.5.
rcp_85  = "rcp85"       # Future period RCP 8.5.
rcp_xx  = "rcpxx"       # Any type of RCP.

# Analysis.
views = {"ts": "Série temporelle", "tbl": "Tableau", "map": "Carte"}
q_list = [0.1, 0.9]

# Paths.
d_data = "./data/"
d_ts   = d_data + "ts/"
d_tbl  = d_data + "tbl/"
d_map  = d_data + "map/"
p_logo = d_data + "ouranos_transparent.png"
p_bounds = d_map + "sn_boundaries.geojson"

# Climate variables (cordex).
var_cordex_tas        = "tas"         # Temperature (daily mean).
var_cordex_tasmin     = "tasmin"      # Temperature (daily minimum).
var_cordex_tasmax     = "tasmax"      # Temperature (daily maximum).
var_cordex_pr         = "pr"          # Precipitation.
var_cordex_uas        = "uas"         # Wind speed, eastward.
var_cordex_vas        = "vas"         # Wind speed, northward.
var_cordex_sfcwindmax = "sfcWindmax"  # Wind speed (daily maximum).
var_cordex_ps         = "ps"          # Barometric pressure.
var_cordex_rsds       = "rsds"        # Solar radiation.
var_cordex_evspsbl    = "evspsbl"     # Evaporation.
var_cordex_evspsblpot = "evspsblpot"  # Potential evapotranspiration.
var_cordex_huss       = "huss"        # Specific humidity.
var_cordex_clt        = "clt"         # Cloud cover.
variables_cordex = [var_cordex_tas, var_cordex_tasmin, var_cordex_tasmax,
                    var_cordex_pr, var_cordex_uas, var_cordex_vas, var_cordex_sfcwindmax,
                    var_cordex_ps, var_cordex_rsds, var_cordex_evspsbl,
                    var_cordex_evspsblpot, var_cordex_huss, var_cordex_clt]

# Climate indices.
idx_etr                    = "etr"
idx_tx90p                  = "tx90p"
idx_heat_wave_max_length   = "heat_wave_max_length"
idx_heat_wave_total_length = "heat_wave_total_len"
idx_hot_spell_frequency    = "hot_spell_frequency"
idx_hot_spell_max_length   = "hot_spell_max_length"
idx_tgg                    = "tgg"
idx_tng                    = "tng"
idx_tnx                    = "tnx"
idx_txg                    = "txg"
idx_txx                    = "txx"
idx_tng_months_below       = "tng_months_below"
idx_tx_days_above          = "tx_days_above"
idx_tn_days_below          = "tn_days_below"
idx_tropical_nights        = "tropical_nights"
idx_wsdi                   = "wsdi"
idx_rx1day                 = "rx1day"
idx_rx5day                 = "rx5day"
idx_cdd                    = "cdd"
idx_cwd                    = "cwd"
idx_dry_days               = "dry_days"
idx_wet_days               = "wet_days"
idx_prcptot                = "prcptot"
idx_r10mm                  = "r10mm"
idx_r20mm                  = "r20mm"
idx_rnnmm                  = "rnnmm"
idx_sdii                   = "sdii"
idx_rain_season            = "rain_season"
idx_rain_season_start      = "rain_season_start"
idx_rain_season_end        = "rain_season_end"
idx_rain_season_length     = "rain_season_length"
idx_rain_season_prcptot    = "rain_season_prcptot"
idx_dry_spell_total_length = "dry_spell_total_length"
idx_wg_days_above          = "wg_days_above"
idx_wx_days_above          = "wx_days_above"
idx_drought_code           = "drought_code"
idx_groups = [[idx_rain_season, [idx_rain_season_start, idx_rain_season_end, idx_rain_season_length,
                                 idx_rain_season_prcptot]]]

# Background color of sidebar.
sb_fill_color = "WhiteSmoke"

# Time series.
cols = {"ref": "black", "rcp26": "blue", "rcp45": "green", "rcp85": "red"}

# Color maps apply to categories of variables and indices.
# +----------------------------+------------+------------+
# | Variable, category         |   Variable |      Index |
# +----------------------------+------------+------------+
# | temperature, high values   | temp_var_1 | temp_idx_1 |
# | temperature, low values    |          - | temp_idx_2 |
# | precipitation, high values | prec_var_1 | prec_idx_1 |
# | precipitation, low values  |          - | prec_idx_2 |
# | precipitation, dates       |          - | prec_idx_3 |
# | wind                       | wind_var_1 | wind_idx_1 |
# +----------------------------+------------+------------+
# The 1st scheme is for absolute values.
# The 2nd scheme is divergent and his made to represent delta values when both negative and positive values are present.
# It combines the 3rd and 4th schemes.
# The 3rd scheme is for negative-only delta values.
# The 4th scheme is for positive-only delta values.
opt_map_col_temp_var   = ["viridis", "RdBu_r", "Blues_r", "Reds"]       # Temperature variables.
opt_map_col_temp_idx_1 = opt_map_col_temp_var                           # Temperature indices (high).
opt_map_col_temp_idx_2 = ["plasma_r", "RdBu", "Reds_r", "Blues"]        # Temperature indices (low).
opt_map_col_prec_var   = ["Blues", "BrWhGr", "Browns_r", "Greens"]      # Precipitation variables.
opt_map_col_prec_idx_1 = opt_map_col_prec_var                           # Precipitation indices (high).
opt_map_col_prec_idx_2 = ["Oranges", "BrWhGr_r", "Greens_r", "Browns"]  # Precipitation indices (low).
opt_map_col_prec_idx_3 = ["viridis", "RdBu_r", "Blues_r", "Reds"]       # Precipitation indices (other).
opt_map_col_wind_var   = ["None", "RdBu_r", "Blues_r", "Reds"]          # Wind variables.
opt_map_col_wind_idx_1 = ["Reds", "RdBu_r", "Blues_r", "Reds"]          # Wind indices.
opt_map_col_default    = ["viridis", "RdBu_r", "Blues_r", "Reds"]       # Other variables and indices.

# Plotting libraries (only for time series).
libs = ["altair", "hvplot", "matplotlib"]

# Discrete vs. continuous colors scales (maps).
opt_map_discrete = True
