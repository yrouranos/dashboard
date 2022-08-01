# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Constants.
#
# Contact information:
# 1. rousseau.yannick@ouranos.ca
# (C) 2020-2022 Ouranos, Canada
# ----------------------------------------------------------------------------------------------------------------------

class Constant:

    # Software version.
    VERSION                  = "1.4.1"

    # Views.
    VIEW_CLUSTER             = "cluster"
    VIEW_CYCLE               = "cycle"
    VIEW_CYCLE_MS            = "cycle_ms"
    VIEW_CYCLE_D             = "cycle_d"
    VIEW_MAP                 = "map"
    VIEW_TAYLOR              = "taylor"
    VIEW_TBL                 = "tbl"
    VIEW_TS                  = "ts"
    VIEW_TS_BIAS             = "ts_bias"

    # Plotting libraries.
    LIB_ALT                  = "alt"
    LIB_HV                   = "hv"
    LIB_MAT                  = "mat"
    LIB_PLY                  = "ply"

    # RCPs.
    REF                      = "ref"
    RCP26                    = "rcp26"
    RCP45                    = "rcp45"
    RCP85                    = "rcp85"
    RCPXX                    = "rcpxx"

    # Statistics.
    STAT_MEAN                = "mean"
    STAT_STD                 = "std"
    STAT_MIN                 = "min"
    STAT_MAX                 = "max"
    STAT_SUM                 = "sum"
    STAT_COUNT               = "count"
    STAT_MEDIAN              = "median"
    STAT_QUANTILE            = "quantile"
    STAT_CENTILE             = "centile"
    STAT_CENTILE_LOWER       = "centile_lower"
    STAT_CENTILE_MIDDLE      = "centile_middle"
    STAT_CENTILE_UPPER       = "centile_upper"

    # Simulations.
    SIMXX                    = "simxx"

    # Platform.
    PLATFORM_SCRIPT          = "script"
    PLATFORM_JUPYTER         = "jupyter"
    PLATFORM_STREAMLIT       = "streamlit"

    # Dataset dimensions.
    DIM_LONGITUDE            = "longitude"
    DIM_LATITUDE             = "latitude"

    # Files.
    F_CSV                    = "csv"                     # CSV file type (comma-separated values).
    F_PNG                    = "png"                     # PNG file type (image).
    F_TIF                    = "tif"                     # TIF file type (image, potentially georeferenced).
    F_NC                     = "nc"                      # NetCDF file type.
    F_NC4                    = "nc4"                     # NetCDF v4 file type.
    F_GEOJSON                = "geojson"                 # GEOJSON file type.
    F_INI                    = "ini"                     # INI file type.
    F_EXT_CSV                = "." + F_CSV               # CSV file extension.
    F_EXT_PNG                = "." + F_PNG               # PNG file extension.
    F_EXT_TIF                = "." + F_TIF               # TIF file extension.
    F_EXT_NC                 = "." + F_NC                # NetCDF file extension.
    F_EXT_NC4                = "." + F_NC4               # NetCDF v4 file extension.
    F_EXT_GEOJSON            = "." + F_GEOJSON           # GEOJSON file extension.
    F_EXT_INI                = "." + F_INI               # INI file extnsion.
    F_EXT_LOG                = ".log"                    # LOG file extension.
    F_LOGO                   = "logo.png"                # Logo file name.
    F_BOUNDS                 = "boundaries.geojson"      # Region boundaries file name.

    # Directories.
    D_DATA                   = "./data/"                 # Path of local directory containing data (dashboard).

    # Data ensembles.
    ENS_CORDEX               = "cordex"                  # CORDEX.
    ENS_ECMWF                = "ecmwf"                   # ECMWF (ENS_ERA5 or ENS_ERA5_LAND).
    ENS_ERA5                 = "era5"                    # ERA5.
    ENS_ERA5_LAND            = "era5_land"               # ERA5-Land.
    ENS_ENACTS               = "enacts"                  # ENACTS.
    ENS_MERRA2               = "merra2"                  # MERRA2.
    ENS_CHIRPS               = "chirps"                  # CHIRPS.

    # Climate variables (CORDEX).
    V_SFTLF                  = "sftlf"                   # Land area fraction.
    V_TAS                    = "tas"                     # Temperature (daily mean).
    V_TASMIN                 = "tasmin"                  # Temperature (daily minimum).
    V_TASMAX                 = "tasmax"                  # Temperature (daily maximum).
    V_PR                     = "pr"                      # Precipitation.
    V_UAS                    = "uas"                     # Wind speed, eastward.
    V_VAS                    = "vas"                     # Wind speed, northward.
    V_SFCWINDMAX             = "sfcWindmax"              # Wind speed (daily maximum).
    V_PS                     = "ps"                      # Barometric pressure.
    V_RSDS                   = "rsds"                    # Solar radiation.
    V_EVSPSBL                = "evspsbl"                 # Evaporation.
    V_EVSPSBLPOT             = "evspsblpot"              # Potential evapotranspiration.
    V_HUSS                   = "huss"                    # Specific humidity.
    V_CLT                    = "clt"                     # Cloud cover.
    V_CORDEX = [V_SFTLF, V_TAS, V_TASMIN, V_TASMAX, V_PR, V_UAS, V_VAS, V_SFCWINDMAX, V_PS, V_RSDS, V_EVSPSBL,
                V_EVSPSBLPOT, V_HUSS, V_CLT]

    # Variables (ECMWF: ERA5 and ERA5-Land).
    V_ECMWF_LSM              = "lsm"                     # Land sea mask.
    V_ECMWF_T2M              = "t2m"                     # Temperature (hourly or daily mean).
    V_ECMWF_T2MMIN           = "t2mmin"                  # Temperature (daily minimum).
    V_ECMWF_T2MMAX           = "t2mmax"                  # Temperature (daily maximum).
    V_ECMWF_TP               = "tp"                      # Precipitation.
    V_ECMWF_U10              = "u10"                     # Wind speed, eastward (hourly or daily mean).
    V_ECMWF_U10MIN           = "u10min"                  # Wind speed, eastward (daily minimum).
    V_ECMWF_U10MAX           = "u10max"                  # Wind speed, eastward (daily maximum).
    V_ECMWF_V10              = "v10"                     # Wind speed, northward (hourly or daily mean).
    V_ECMWF_V10MIN           = "v10min"                  # Wind speed, northward (daily minimum).
    V_ECMWF_V10MAX           = "v10max"                  # Wind speed, northward (daily maximum).
    V_ECMWF_UV10             = "uv10"                    # Wind speed (hourly or daily mean).
    V_ECMWF_UV10MIN          = "uv10min"                 # Wind speed (daily minimum).
    V_ECMWF_UV10MAX          = "uv10max"                 # Wind speed (daily maximum).
    V_ECMWF_SP               = "sp"                      # Barometric pressure.
    V_ECMWF_SSRD             = "ssrd"                    # Solar radiation.
    V_ECMWF_E                = "e"                       # Evaporation.
    V_ECMWF_PEV              = "pev"                     # Potential evapotranspiration.
    V_ECMWF_D2M              = "d2m"                     # Dew temperature.
    V_ECMWF_SH               = "sh"                      # Specific humidity.
    V_ECMWF = [V_ECMWF_LSM, V_ECMWF_T2M, V_ECMWF_T2MMIN, V_ECMWF_T2MMAX, V_ECMWF_TP, V_ECMWF_U10,
               V_ECMWF_U10MIN, V_ECMWF_U10MAX, V_ECMWF_V10, V_ECMWF_V10MIN, V_ECMWF_V10MAX, V_ECMWF_UV10,
               V_ECMWF_UV10MIN, V_ECMWF_UV10MAX, V_ECMWF_SP, V_ECMWF_SSRD, V_ECMWF_E, V_ECMWF_PEV, V_ECMWF_D2M,
               V_ECMWF_SH]

    # Variables (ENACTS).
    V_ENACTS_TMIN            = "tmin"                    # Temperature (daily minimum).
    V_ENACTS_TMAX            = "tmax"                    # Temperature (daily maximum).
    V_ENACTS_RR              = "rr"                      # Precipitation.
    V_ENACTS_PET             = "pet"                     # Potential evapotranspiration.
    V_ENACTS = [V_ENACTS_TMIN, V_ENACTS_TMAX, V_ENACTS_RR, V_ENACTS_PET]

    # Variables (CHIRPS).
    V_CHIRPS_PRECIP          = "precip"                  # Precipitation.
    V_CHIRPS = [V_CHIRPS_PRECIP]

    # Climate indices (temperature)
    I_ETR                    = "etr"                     # Extreme temperature range.
    I_TGG                    = "tgg"                     # Mean of mean temperature.
    I_TNG                    = "tng"                     # Mean of minimum temperature
    I_TNX                    = "tnx"                     # Maximum of minimum temperature.
    I_TXG                    = "txg"                     # Mean of maximum temperature
    I_TXX                    = "txx"                     # Maximum of maximum temperature
    I_TX90P                  = "tx90p"                   # Number of days with extreme maximum temp. (> 90th pct.).
    I_TNG_MONTHS_BELOW       = "tng_months_below"        # Months per year with a mean minimum temp. < X.
    I_TX_DAYS_ABOVE          = "tx_days_above"           # Days per year with maximum temperature > X.
    I_TN_DAYS_BELOW          = "tn_days_below"           # Days per year with a minimum temperature < X.
    I_TROPICAL_NIGHTS        = "tropical_nights"         # Tropical nights per year, i.e. with minimum temp. > X.
    I_HEAT_WAVE_MAX_LENGTH   = "heat_wave_max_length"    # Maximum heat wave length.
    I_HEAT_WAVE_TOTAL_LENGTH = "heat_wave_total_length"  # Total heat wave length.
    I_HOT_SPELL_FREQUENCY    = "hot_spell_frequency"     # Number of hot spells.
    I_HOT_SPELL_MAX_LENGTH   = "hot_spell_max_length"    # Maximum length of hot spells.
    I_HOT_SPELL_TOTAL_LENGTH = "hot_spell_total_length"  # Total length of hor spells.

    # Climate indices (precipitation).
    I_WSDI                   = "wsdi"                    # Warm spell duration index.
    I_RX1DAY                 = "rx1day"                  # Largest 1-day precipitation amount.
    I_RX5DAY                 = "rx5day"                  # Largest 5-day precipitation amount.
    I_CDD                    = "cdd"                     # Maximum number of consecutive dry days.
    I_CWD                    = "cwd"                     # Maximum number of consecutive wet days.
    I_DRY_DAYS               = "dry_days"                # Number of days with prpecipitation < X mm.
    I_WET_DAYS               = "wet_days"                # Number of days with precipitation ≥ X mm.
    I_PRCPTOT                = "prcptot"                 # Accumulated total precipitation.
    I_R10MM                  = "r10mm"                   # Number of days with precipitation ≥ 10 mm.
    I_R20MM                  = "r20mm"                   # Number of days with precipitation ≥ 20 mm.
    I_SDII                   = "sdii"                    # Mean daily precipitation intensity.
    I_RAIN_SEASON            = "rain_season"             # Rain season.
    I_RAIN_SEASON_START      = "rain_season_start"       # Day of year on which rain season starts.
    I_RAIN_SEASON_END        = "rain_season_end"         # Day of year on which rain season ends.
    I_RAIN_SEASON_LENGTH     = "rain_season_length"      # Duration of the rain season.
    I_RAIN_SEASON_PRCPTOT    = "rain_season_prcptot"     # Quantity received during rain season.
    I_DRY_SPELL_TOTAL_LENGTH = "dry_spell_total_length"  # Total length of dry period.

    # Climate indices (temperature and precipitation).
    I_DROUGHT_CODE           = "drought_code"            # Drought code.

    # Climate indices (wind).
    I_WG_DAYS_ABOVE          = "wg_days_above"           # Days per year with mean wind speed > X and direction D.
    I_WX_DAYS_ABOVE          = "wx_days_above"           # Days per year with maximum wind speed > X.

    # Groups of indices.
    i_groups = {I_RAIN_SEASON: [I_RAIN_SEASON_START, I_RAIN_SEASON_END, I_RAIN_SEASON_LENGTH, I_RAIN_SEASON_PRCPTOT]}

    # List of indices.
    indices = [I_ETR, I_TGG, I_TNG, I_TNX, I_TXG, I_TXX, I_TX90P, I_TNG_MONTHS_BELOW, I_TX_DAYS_ABOVE, I_TN_DAYS_BELOW,
               I_TROPICAL_NIGHTS, I_HEAT_WAVE_MAX_LENGTH, I_HEAT_WAVE_TOTAL_LENGTH, I_HOT_SPELL_FREQUENCY,
               I_HOT_SPELL_MAX_LENGTH, I_HOT_SPELL_TOTAL_LENGTH, I_WSDI, I_RX1DAY, I_RX5DAY, I_CDD, I_CWD, I_DRY_DAYS,
               I_WET_DAYS, I_PRCPTOT, I_R10MM, I_R20MM, I_SDII, I_RAIN_SEASON, I_RAIN_SEASON_START, I_RAIN_SEASON_END,
               I_RAIN_SEASON_LENGTH, I_RAIN_SEASON_PRCPTOT, I_DRY_SPELL_TOTAL_LENGTH, I_DROUGHT_CODE, I_WG_DAYS_ABOVE,
               I_WX_DAYS_ABOVE]

    # Debug parameters.
    # Not all parameters need/can be specified.
    DBG              = False            # If "True", enable dashboard debugging (in 'dash.py').
    DBG_PROJECT_CODE = ""               # Project code: "<country>-<region>-<obs_src>"
    DBG_VIEW_CODE    = ""               # View code: {VIEW_TS, VIEW_TS_BIAS, VIEW_TBL, VIEW_MAP, VIEW_CYCLE_MS,
                                        # VIEW_CYCLE_D, VIEW_CLUSTER}
    DBG_LIB_CODE     = ""               # Library code: {LIB_ALT, LIB_HV, LIB_MAT, LIB_PLY}
    DBG_DELTA_CODE   = ""               # If "True", calculate anomalies. If "False", calculate absolute values.
    DBG_VI_CODE      = ""               # Select a variable from 'V_CORDEX'.
    DBG_HOR_CODE     = []               # Period: [<year_1>, <year_n>]
    DBG_RCP_CODE     = ""               # Emission scenario: {REF, RCP26, RCP45, RCP85, RCPXX}
    DBG_STAT_CODE    = ""               # Statistic code: {STAT_MEAN, <centile_code>}
                                        # Example of <centile_code>: "c010" for the 10th centile.


const = Constant()
