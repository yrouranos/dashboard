# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Constants.
#
# Contact information:
# 1. rousseau.yannick@ouranos.ca
# (C) 2020-2022 Ouranos, Canada
# ----------------------------------------------------------------------------------------------------------------------

class Constant:

    # Views.
    view_ts                  = "ts"
    view_ts_bias             = "ts_bias"
    view_tbl                 = "tbl"
    view_map                 = "map"
    view_cycle               = "cycle"
    view_cycle_ms            = "cycle_ms"
    view_cycle_d             = "cycle_d"

    # Plotting libraries.
    lib_alt                  = "alt"
    lib_hv                   = "hv"
    lib_mat                  = "mat"
    lib_ply                  = "ply"

    # RCPs.
    ref                      = "ref"
    rcp26                    = "rcp26"
    rcp45                    = "rcp45"
    rcp85                    = "rcp85"
    rcpxx                    = "rcpxx"

    # Statistics.
    stat_min                 = "min"
    stat_q_low               = "q10"
    stat_median              = "median"
    stat_q_high              = "q90"
    stat_max                 = "max"
    stat_mean                = "mean"
    stat_sum                 = "sum"
    stat_quantile            = "quantile"

    # Simulations.
    simxx                    = "simxx"

    # Platform.
    platform_script          = "script"
    platform_jupyter         = "jupyter"
    platform_streamlit       = "streamlit"

    # Files.
    f_csv                    = "csv"                     # CSV file type (comma-separated values).
    f_png                    = "png"                     # PNG file type (image).
    f_tif                    = "tif"                     # TIF file type (image, potentially georeferenced).
    f_nc                     = "nc"                      # NetCDF file type.
    f_nc4                    = "nc4"                     # NetCDF v4 file type.
    f_ext_csv                = "." + f_csv               # CSV file extension.
    f_ext_png                = "." + f_png               # PNG file extension.
    f_ext_tif                = "." + f_tif               # TIF file extension.
    f_ext_nc                 = "." + f_nc                # NetCDF file extension.
    f_ext_nc4                = "." + f_nc4               # NetCDF v4 file extension.
    f_ext_log                = ".log"                    # LOG file extension.

    # Data ensembles.
    ens_cordex               = "cordex"                  # CORDEX.
    ens_era5                 = "era5"                    # ERA5.
    ens_era5_land            = "era5_land"               # ERA5-Land.
    ens_enacts               = "enacts"                  # ENACTS.
    ens_merra2               = "merra2"                  # MERRA2.

    # Climate variables (CORDEX).
    v_tas                    = "tas"                     # Temperature (daily mean).
    v_tasmin                 = "tasmin"                  # Temperature (daily minimum).
    v_tasmax                 = "tasmax"                  # Temperature (daily maximum).
    v_pr                     = "pr"                      # Precipitation.
    v_uas                    = "uas"                     # Wind speed, eastward.
    v_vas                    = "vas"                     # Wind speed, northward.
    v_sfcwindmax             = "sfcWindmax"              # Wind speed (daily maximum).
    v_ps                     = "ps"                      # Barometric pressure.
    v_rsds                   = "rsds"                    # Solar radiation.
    v_evspsbl                = "evspsbl"                 # Evaporation.
    v_evspsblpot             = "evspsblpot"              # Potential evapotranspiration.
    v_huss                   = "huss"                    # Specific humidity.
    v_clt                    = "clt"                     # Cloud cover.
    variables = [v_tas, v_tasmin, v_tasmax, v_pr, v_uas, v_vas, v_sfcwindmax, v_ps, v_rsds, v_evspsbl, v_evspsblpot,
                 v_huss, v_clt]

    # Variables (ERA5; ERA5-Land).
    v_era5_t2m               = "t2m"                     # Temperature (hourly or daily mean).
    v_era5_t2mmin            = "t2mmin"                  # Temperature (daily minimum).
    v_era5_t2mmax            = "t2mmax"                  # Temperature (daily maximum).
    v_era5_tp                = "tp"                      # Precipitation.
    v_era5_u10               = "u10"                     # Wind speed, eastward (hourly or daily mean).
    v_era5_u10min            = "u10min"                  # Wind speed, eastward (daily minimum).
    v_era5_u10max            = "u10max"                  # Wind speed, eastward (daily maximum).
    v_era5_v10               = "v10"                     # Wind speed, northward (hourly or daily mean).
    v_era5_v10min            = "v10min"                  # Wind speed, northward (daily minimum).
    v_era5_v10max            = "v10max"                  # Wind speed, northward (daily maximum).
    v_era5_uv10              = "uv10"                    # Wind speed (hourly or daily mean).
    v_era5_uv10min           = "uv10min"                 # Wind speed (daily minimum).
    v_era5_uv10max           = "uv10max"                 # Wind speed (daily maximum).
    v_era5_sp                = "sp"                      # Barometric pressure.
    v_era5_ssrd              = "ssrd"                    # Solar radiation.
    v_era5_e                 = "e"                       # Evaporation.
    v_era5_pev               = "pev"                     # Potential evapotranspiration.
    v_era5_d2m               = "d2m"                     # Dew temperature.
    v_era5_sh                = "sh"                      # Specific humidity.
    variables_era5 = [v_era5_t2m, v_era5_t2mmin, v_era5_t2mmax, v_era5_tp, v_era5_u10, v_era5_u10min, v_era5_u10max,
                      v_era5_v10, v_era5_v10min, v_era5_v10max, v_era5_uv10, v_era5_uv10min, v_era5_uv10max, v_era5_sp,
                      v_era5_ssrd, v_era5_e, v_era5_pev, v_era5_d2m, v_era5_sh]

    # Variables (ENACTS).
    v_enacts_tmin            = "tmin"                    # Temperature (daily minimum).
    v_enacts_tmax            = "tmax"                    # Temperature (daily maximum).
    v_enacts_rr              = "rr"                      # Precipitation.
    v_enacts_pet             = "pet"                     # Potential evapotranspiration.
    variables_enacts = [v_enacts_tmin, v_enacts_tmax, v_enacts_rr, v_enacts_pet]

    # Climate indices (temperature)
    i_etr                    = "etr"                     # Extreme temperature range.
    i_tgg                    = "tgg"                     # Mean of mean temperature.
    i_tng                    = "tng"                     # Mean of minimum temperature
    i_tnx                    = "tnx"                     # Maximum of minimum temperature.
    i_txg                    = "txg"                     # Mean of maximum temperature
    i_txx                    = "txx"                     # Maximum of maximum temperature
    i_tx90p                  = "tx90p"                   # Number of days with extreme maximum temp. (> 90th pct.).
    i_tng_months_below       = "tng_months_below"        # Months per year with a mean minimum temp. < X.
    i_tx_days_above          = "tx_days_above"           # Days per year with maximum temperature > X.
    i_tn_days_below          = "tn_days_below"           # Days per year with a minimum temperature < X.
    i_tropical_nights        = "tropical_nights"         # Tropical nights per year, i.e. with minimum temp. > X.
    i_heat_wave_max_length   = "heat_wave_max_length"    # Maximum heat wave length.
    i_heat_wave_total_length = "heat_wave_total_len"     # Total heat wave length.
    i_hot_spell_frequency    = "hot_spell_frequency"     # Number of hot spells.
    i_hot_spell_max_length   = "hot_spell_max_length"    # Maximum hot spell length

    # Climate indices (precipitation).
    i_wsdi                   = "wsdi"                    # Warm spell duration index.
    i_rx1day                 = "rx1day"                  # Largest 1-day precipitation amount.
    i_rx5day                 = "rx5day"                  # Largest 5-day precipitation amount.
    i_cdd                    = "cdd"                     # Maximum number of consecutive dry days.
    i_cwd                    = "cwd"                     # Maximum number of consecutive wet days.
    i_dry_days               = "dry_days"                # Number of dry days.
    i_wet_days               = "wet_days"                # Number of wet days.
    i_prcptot                = "prcptot"                 # Accumulated total precipitation.
    i_r10mm                  = "r10mm"                   # Number of days with precipitation ≥ 10 mm.
    i_r20mm                  = "r20mm"                   # Number of days with precipitation ≥ 20 mm.
    i_rnnmm                  = "rnnmm"                   # Number of days with precipitation ≥ X mm.
    i_sdii                   = "sdii"                    # Mean daily precipitation intensity.
    i_rain_season            = "rain_season"             # Rain season.
    i_rain_season_start      = "rain_season_start"       # Day of year on which rain season starts.
    i_rain_season_end        = "rain_season_end"         # Day of year on which rain season ends.
    i_rain_season_length     = "rain_season_length"      # Duration of the rain season.
    i_rain_season_prcptot    = "rain_season_prcptot"     # Quantity received during rain season.
    i_dry_spell_total_length = "dry_spell_total_length"  # Total length of dry period.

    # Climate indices (temperature and precipitation).
    i_drought_code           = "drought_code"            # Drought code.

    # Climate indices (wind).
    i_wg_days_above          = "wg_days_above"           # Days per year with mean wind speed > X and direction D.
    i_wx_days_above          = "wx_days_above"           # Days per year with maximum wind speed > X.

    # Groups of indices.
    i_groups = {i_rain_season: [i_rain_season_start, i_rain_season_end, i_rain_season_length, i_rain_season_prcptot]}

    # List of indices.
    indices = [i_etr, i_tgg, i_tng, i_tnx, i_txg, i_txx, i_tx90p, i_tng_months_below, i_tx_days_above, i_tn_days_below,
               i_tropical_nights, i_heat_wave_max_length, i_heat_wave_total_length, i_hot_spell_frequency,
               i_hot_spell_max_length, i_wsdi, i_rx1day, i_rx5day, i_cdd, i_cwd, i_dry_days, i_wet_days, i_prcptot,
               i_r10mm, i_r20mm, i_rnnmm, i_sdii, i_rain_season, i_rain_season_start, i_rain_season_end,
               i_rain_season_length, i_rain_season_prcptot, i_dry_spell_total_length, i_drought_code, i_wg_days_above,
               i_wx_days_above, i_rain_season]


const = Constant()
