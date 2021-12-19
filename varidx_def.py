# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: RCP and RCPs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import context_def
import glob
import object_def
import os
import dash_utils
import view_def
from typing import List, Union


# Data ensembles -------------------------------------------------------------------------------------------------------

ens_cordex                 = "cordex"                  # CORDEX.
ens_era5                   = "era5"                    # ERA5.
ens_era5_land              = "era5_land"               # ERA5-Land.
ens_enacts                 = "enacts"                  # ENACTS.
ens_merra2                 = "merra2"                  # MERRA2.

# Climate variables (CORDEX) -------------------------------------------------------------------------------------------

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
variables = [v_tas, v_tasmin, v_tasmax, v_pr, v_uas, v_vas, v_sfcwindmax, v_ps, v_rsds, v_evspsbl, v_evspsblpot, v_huss,
             v_clt]

# Variables (ERA5; ERA5-Land) ------------------------------------------------------------------------------------------

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

# Variables (ENACTS) ---------------------------------------------------------------------------------------------------

v_enacts_tmin            = "tmin"                    # Temperature (daily minimum).
v_enacts_tmax            = "tmax"                    # Temperature (daily maximum).
v_enacts_rr              = "rr"                      # Precipitation.
v_enacts_pet             = "pet"                     # Potential evapotranspiration.
variables_enacts = [v_enacts_tmin, v_enacts_tmax, v_enacts_rr, v_enacts_pet]

# Climate indices ------------------------------------------------------------------------------------------------------

# Temperature-related.
i_etr                    = "etr"                     # Extreme temperature range.
i_tgg                    = "tgg"                     # Mean of mean temperature.
i_tng                    = "tng"                     # Mean of minimum temperature
i_tnx                    = "tnx"                     # Maximum of minimum temperature.
i_txg                    = "txg"                     # Mean of maximum temperature
i_txx                    = "txx"                     # Maximum of maximum temperature
i_tx90p                  = "tx90p"                   # Number of days with extreme maximum temperature (> 90th pct.).
i_tng_months_below       = "tng_months_below"        # Months per year with a mean minimum temperature < X.
i_tx_days_above          = "tx_days_above"           # Days per year with maximum temperature > X.
i_tn_days_below          = "tn_days_below"           # Days per year with a minimum temperature < X.
i_tropical_nights        = "tropical_nights"         # Tropical nights per year, i.e. with minimum temperature > X.
i_heat_wave_max_length   = "heat_wave_max_length"    # Maximum heat wave length.
i_heat_wave_total_length = "heat_wave_total_len"     # Total heat wave length.
i_hot_spell_frequency    = "hot_spell_frequency"     # Number of hot spells.
i_hot_spell_max_length   = "hot_spell_max_length"    # Maximum hot spell length

# Precipitation-related.
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

# Temperature-precipitation-related.
i_drought_code  = "drought_code"   # Drought code.

# Wind-related.
i_wg_days_above = "wg_days_above"  # Days per year with mean wind speed > X, with a given direction.
i_wx_days_above = "wx_days_above"  # Days per year with maximum wind speed > X.

# Groups of indices.
i_groups = [[i_rain_season, [i_rain_season_start, i_rain_season_end, i_rain_season_length, i_rain_season_prcptot]]]

# List of indices.
indices = [i_etr, i_tgg, i_tng, i_tnx, i_txg, i_txx, i_tx90p, i_tng_months_below, i_tx_days_above, i_tn_days_below,
           i_tropical_nights, i_heat_wave_max_length, i_heat_wave_total_length, i_hot_spell_frequency,
           i_hot_spell_max_length, i_wsdi, i_rx1day, i_rx5day, i_cdd, i_cwd, i_dry_days, i_wet_days, i_prcptot,
           i_r10mm, i_r20mm, i_rnnmm, i_sdii, i_rain_season, i_rain_season_start, i_rain_season_end,
           i_rain_season_length, i_rain_season_prcptot, i_dry_spell_total_length, i_drought_code, i_wg_days_above,
           i_wx_days_above, i_rain_season]

# Properties of variables and indices-----------------------------------------------------------------------------------

# TODO: Could replace X,Y,Z with threshold values with the information in the configuration file.

# Properties of variables and indices.
# Cell 1: Long description
# Cell 2: Short description (for y-label).
# Cell 3: Units.
# Cell 4: Precision (number of decimal places to show).
code_props = {

    # Variables (CORDEX):
    v_tas:                    ["Température moyenne",              "Température",           "°C",    1],
    v_tasmin:                 ["Température minimale journalière", "Température",           "°C",    1],
    v_tasmax:                 ["Température maximale journalière", "Température",           "°C",    1],
    v_uas:                    ["Vitesse du vent (dir. est)",       "Vitesse",               "km/h",  0],
    v_vas:                    ["Vitesse du vent (dir. nord)",      "Vitesse",               "km/h",  0],
    v_sfcwindmax:             ["Vitesse du vent",                  "Vitesse",               "km/h",  0],
    v_ps:                     ["Pression barométrique",            "Pression barométrique", "Pa",    0],
    v_rsds:                   ["Radiation solaire",                "Radiation solaire",     "Pa",    0],
    v_pr:                     ["Précipitation",                    "Cumul",                 "mm",    0],
    v_evspsbl:                ["Évapotranspiration",               "Cumul",                 "mm",    0],
    v_evspsblpot:             ["Évapotranspiration potentielle",   "Cumul",                 "mm",    0],
    v_huss:                   ["Humidité spécifique",              "Humidité spécifique",   "",      2],
    v_clt:                    ["Couvert nuageux",                  "Couvert nuageux",       "%",     1],

    # Variables (ERA5 and ERA5-Land):
    v_era5_d2m:               ["Point de rosée",                   "Point de rosée",        "",      1],
    v_era5_t2m:               ["Température moyenne",              "Température",           "°C",    1],
    v_era5_sp:                ["Pression barométrique",            "Pression barométrique", "Pa",    0],
    v_era5_tp:                ["Précipitation",                    "Cumul",                 "mm",    0],
    v_era5_u10:               ["Vitesse du vent (dir. est)",       "Vitesse",               "km/h",  0],
    v_era5_v10:               ["Vitesse du vent (dir. nord)",      "Vitesse",               "km/h",  0],
    v_era5_ssrd:              ["Radiation solaire",                "Radiation solaire",     "Pa",    0],
    v_era5_e:                 ["Évapration",                       "Cumul",                 "mm",    0],
    v_era5_pev:               ["Évapotranspiration potentielle",   "Cumul",                 "mm",    0],
    v_era5_sh:                ["Humidité spécifique",              "Humidité spécifique",   "",      2],

    # Variables (ENACTS):
    v_enacts_tmin:            ["Température minimale journalière", "Température",           "°C",    1],
    v_enacts_tmax:            ["Température maximale journalière", "Température",           "°C",    1],
    v_enacts_rr:              ["Précipitation",                    "Cumul",                 "mm",    0],
    v_enacts_pet:             ["Évapotranspiration potentielle",   "Cumul",                 "mm",    0],

    # Indices:
    i_etr:                    ["Écart extrême de température",     "Température",           "°C",    1],
    i_tx90p:                  ["Nombre de jours chauds (Tmax > 90e percentile)", "Nbr. jours", "jours", 0],
    i_heat_wave_max_length:   ["Durée maximale des vagues de chaleur", "Durée", "jours", 0],
    i_heat_wave_total_length: ["Durée totale des vagues de chaleur", "Durée", "jours", 0],
    i_hot_spell_frequency:    ["Nombre de périodes chaudes", "Nbr. périodes", "périodes", 0],
    i_hot_spell_max_length:   ["Durée maximale des périodes chaudes", "Durée", "jours", 0],
    i_tgg:                    ["Température moyenne calculée à partir de Tmin et Tmax", "Température", "°C", 1],
    i_tng:                    ["Nbr mois frais (moyenne mensuelle de Tmin < X°C)", "Nbr. mois", "mois", 1],
    i_tnx:                    ["Valeur maximale de Tmin", "Température", "°C", 1],
    i_txg:                    ["Valeur moyenne de Tmax", "Température", "°C", 1],
    i_tng_months_below:       ["Nombre de mois frais", "Nbr. mois", "", 1],
    i_tx_days_above:          ["Nombre de jours chauds (Tmax > X°C)", "Nbr. jours", "jours", 0],
    i_tn_days_below:          ["Nombre de jours frais (Tmin < X°C)", "Nbr. jours", "jours", 0],
    i_tropical_nights:        ["Nombre de nuits chaudes (Tmin > X°C)", "Nbr. jours", "jours", 0],
    i_wsdi:                   ["Indice de durée des périodes chaudes (Tmax ≥ X; Y jours consécutifs)",
                               "Indice", "", 0],
    i_rx1day:                 ["Cumul de précipitations (1 jour)", "Cumul", "mm", 0],
    i_rx5day:                 ["Cumul de précipitations (5 jours)", "Cumul", "mm", 0],
    i_cdd:                    ["Nombre de jours secs consécutifs (P < X mm)", "Nbr. jours", "jours", 0],
    i_cwd:                    ["Nombre de jours pluvieux consécutifs (P ≥ X mm)", "Nbr. jours", "jours", 0],
    i_dry_days:               ["Nombre de jours secs (P < X mm)", "Nbr. jours", "jours", 0],
    i_wet_days:               ["Nombre de jours pluvieux (P ≥ X mm)", "Nbr. jours", "jours", 0],
    i_prcptot:                ["Cumul de précipitation (entre les jours X et Y)", "Cumul", "mm", 0],
    i_r10mm:                  ["Nombre de jours avec P ≥ 10 mm", "Nbr. jours", "jours", 0],
    i_r20mm:                  ["Nombre de jours avec P ≥ 20 mm", "Nbr. jours", "jours", 0],
    i_rnnmm:                  ["Nombre de jours avec P ≥ X mm", "Nbr. jours", "jours", 0],
    i_sdii:                   ["Intensité moyenne des précipitations", "Intensité", "mm/day", 0],
    i_rain_season_start:      ["Début de la saison de pluie", "Jour", "", 0],
    i_rain_season_end:        ["Fin de la saison de pluie", "Jour", "", 0],
    i_rain_season_length:     ["Durée de la saison de pluie", "Nbr. Jours", "jours", 0],
    i_rain_season_prcptot:    ["Cumul de précipitation pendant la saison de pluie", "Cumul", "mm", 0],
    i_dry_spell_total_length: ["Durée totale des périodes sèches (P < X mm/jour; Y jours consécutifs)",
                               "Nbr. jours", "jours", 0],
    i_wg_days_above:          ["Nombre de jours avec vent fort (Vmoy ≥ X km/h)", "Nbr. jours", "jours", 0],
    i_wx_days_above:          ["Nombre de jours avec vent fort directionel (Vmax ≥ X km/h; direction de Y±Z°)",
                               "Nbr. jours", "jours", 0],
    i_drought_code:           ["Code de sécheresse", "Code", "", 0]
}


def get_group(
    idx_item: str = ""
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the name of a group of indices.

    Parameters
    ----------
    idx_item : str, optional
        Group name.
    --------------------------------------------------------------------------------------------------------------------
    """

    group = idx_item

    for i in range(len(i_groups)):

        if idx_item in i_groups[i][1]:
            group = i_groups[i][0] + idx_item.replace(idx_item, "")
            break

    return group


class VarIdx(object_def.Obj):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object VarIdx.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    def __init__(
        self,
        code
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        desc = "" if code == "" else code_props[code][0]
        super(VarIdx, self).__init__(code=code, desc=desc)
    
    def get_name(
        self
    ) -> str:

        """
        ----------------------------------------
        Extract name.

        Returns
        -------
        str
            Name.
        ----------------------------------------
        """

        pos = self.code.rfind("_")
        if pos >= 0:
            tokens = self.code.split("_")
            if tokens[len(tokens) - 1].isdigit():
                return self.code[0:pos]

        return self.code
    
    def get_unit(
        self
    ) -> str:
    
        """
        ----------------------------------------
        Get unit.

        Returns
        -------
        str
            Unit.
        ----------------------------------------
        """

        return code_props[self.get_code()][2]

    def get_precision(
        self
    ) -> int:

        """
        ----------------------------------------
        Get precision (number of decimals).

        Returns
        -------
        int
            Precision (number of decimals).
        ----------------------------------------
        """

        return code_props[self.get_code()][3]

    def get_label(
        self
    ) -> str:

        """
        ----------------------------------------
        Combine description and unit.

        Returns
        -------
        str
            Combine description and unit.
        ----------------------------------------
        """

        desc = code_props[self.get_code()][1]
        unit = str(self.get_unit())
        if (unit not in ["", "1"]) and (unit not in desc):
            unit = " (" + unit + ")"
        
        return desc + unit
    
    def is_var(
        self
    ) -> bool:
        
        """
        ----------------------------------------
        Determine if the instance is a variable.
        ----------------------------------------
        """

        return self.get_ens() in [ens_cordex, ens_era5, ens_era5_land, ens_merra2, ens_enacts]

    def get_ens(
        self
    ) -> str:

        """
        ----------------------------------------
        Get ensemble name.

        Returns
        -------
        str
            Ensemble name.
        ----------------------------------------
        """

        ens = ""

        # CORDEX.
        if self.get_name() in variables:
            ens = ens_cordex

        # ERA5 and ERA5-Land.
        elif self.get_name() in variables_era5:
            ens = ens_era5

        # ENACTS.
        elif self.get_name() in variables_enacts:
            ens = ens_enacts

        return ens

    def convert_name(
        self,
        ens_code: str
    ) -> Union[any, str]:

        """
        ----------------------------------------
        Convert from CORDEX variable name to the equivalent variable name in another set (ERA5*, ENACTS)
        (or the opposite).

        Parameters
        ----------
        ens_code : str
            Data ensemble code.
        ----------------------------------------
        """

        # Equivalences.
        equi = [[v_tas,        v_era5_t2m,     ""],
                [v_tasmin,     v_era5_t2mmin,  v_enacts_tmin],
                [v_tasmax,     v_era5_t2mmax,  v_enacts_tmax],
                [v_pr,         v_era5_tp,      v_enacts_rr],
                [v_uas,        v_era5_u10,     ""],
                [v_vas,        v_era5_v10,     ""],
                [v_sfcwindmax, v_era5_uv10max, ""],
                [v_ps,         v_era5_sp,      ""],
                [v_rsds,       v_era5_ssrd,    ""],
                [v_evspsbl,    v_era5_e,       ""],
                [v_evspsblpot, v_era5_pev,     v_enacts_pet],
                [v_huss,       v_era5_sh,      ""]]

        # Loop through equivalences.
        for i in range(len(equi)):

            # Verify if there is a match.
            if self.get_name in equi[i]:
                if self.get_ens() == ens_cordex:
                    if ens_code in [ens_era5, ens_era5_land]:
                        return equi[i][1]
                    elif ens_code == ens_enacts:
                        return equi[i][2]
                else:
                    return equi[i][0]

        return None


class VarIdxs(object_def.Objs):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object VarIdxs.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        *args
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super().__init__()

        if len(args) > 0:
            if isinstance(args[0], context_def.Context):
                self.load(args)
            else:
                self.add(args[0])

    def load(
        self,
        args
    ):

        """
        ----------------------------------------
        Load items.

        Parameters
        ----------
        args :
            args[0] : cntx: context_def.Context
                Context.
        ----------------------------------------
        """

        cntx = args[0]
        
        code_l = []

        # The items are extracted from directory names.
        # ~/<project_code>/<view_code>/*
        if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>/*.csv"
            p = p.replace("<view_code>/", cntx.view.get_code().split("-")[0] + "*/")
            for p_i in list(glob.glob(p)):
                code = os.path.basename(p_i).replace(".csv", "")
                if code not in code_l:
                    code_l.append(code)

        # The items are extracted from directory names.
        # ~/<project_code>/<view_code>/<varidx_code>/*
        elif cntx.view.get_code() in [view_def.mode_map, view_def.mode_cycle]:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>*/*"
            p = p.replace("<view_code>", cntx.view.get_code())
            for p_i in list(glob.glob(p)):
                code = os.path.basename(p_i)
                if (code not in code_l) and (os.path.isdir(p_i)):
                    code_l.append(code)
        code_l.sort()

        self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        code : Union[str, List[str]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(VarIdx(code_l[i]))

        return super(VarIdxs, self).add_items(items, inplace)

    def get_desc_l(
        self
    ) -> List[str]:

        """
        ----------------------------------------
        Get a list of descriptions.

        Returns
        -------
        List[str]
            Descriptions.
        ----------------------------------------
        """

        desc_l = super(VarIdxs, self).get_desc_l()
        desc_l.sort()

        return desc_l
