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

import config as cf
import glob
import math
import object_def
import os
import utils
import view_def
from typing import List


"""
Climate variables (CORDEX) ---------------------------------------------------------------------------------------------
"""

# Temperature (daily mean).
var_tas = "tas"

# Temperature (daily minimum).
var_tasmin = "tasmin"

# Temperature (daily maximum).
var_tasmax = "tasmax"

# Precipitation.
var_pr = "pr"

# Wind speed, eastward.
var_uas = "uas"

# Wind speed, northward.
var_vas = "vas"

# Wind speed (daily maximum).
var_sfcwindmax = "sfcWindmax"

# Barometric pressure.
var_ps = "ps"

# Solar radiation.
var_rsds = "rsds"

# Evaporation.
var_evspsbl = "evspsbl"

# Potential evapotranspiration.
var_evspsblpot = "evspsblpot"

# Specific humidity.
var_huss = "huss"

# Cloud cover.
var_clt = "clt"

# All variables.
vars = [var_tas, var_tasmin, var_tasmax, var_pr, var_uas, var_vas, var_sfcwindmax,
        var_ps, var_rsds, var_evspsbl, var_evspsblpot, var_huss, var_clt]
            
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
-------------------------------------------------------------------------------------------------------------------------
"""

# TODO: Replace X and Y by real values.
# Properties of variables and indices.
code_props = {
    var_tas:                    ["Température moyenne",
                                 "Température",
                                 "°C"],
    var_tasmin:                 ["Température minimale quotidienne",
                                 "Température",
                                 "°C"],
    var_tasmax:                 ["Température maximale quotidienne",
                                 "Température",
                                 "°C"],
    var_uas:                    ["Vitesse du vent (dir. est)",
                                 "Vitesse",
                                 "km/h"],
    var_vas:                    ["Vitesse du vent (dir. nord)",
                                 "Vitesse",
                                 "km/h"],
    var_sfcwindmax:             ["Vitesse du vent",
                                 "Vitesse",
                                 "km/h"],
    var_ps:                     ["Pression barométrique",
                                 "Pression barométrique",
                                 "Pa"],
    var_rsds:                   ["Radiation solaire",
                                 "Radiation solaire",
                                 "Pa"],
    var_pr:                     ["Précipitation",
                                 "Cumul",
                                 "mm"],
    var_evspsbl:                ["Évapotranspiration",
                                 "Cumul.",
                                 "mm"],
    var_evspsblpot:             ["Évapotranspiration potentielle",
                                 "Cumul",
                                 "mm"],
    var_huss:                   ["Humidité spécifique",
                                 "Humidité spécifique",
                                 ""],
    var_clt:                    ["Couvert nuageux",
                                 "Couvert nuageux",
                                 "%"],
    idx_etr:                    ["Écart extrême de température",
                                 "Température",
                                 "°C"],
    idx_tx90p:                  ["Nombre de jours chauds (Tmax > 90e percentile)",
                                 "Nbr. jours",
                                 "jours"],
    idx_heat_wave_max_length:   ["Durée maximale des vagues de chaleur",
                                 "Durée",
                                 "jours"],
    idx_heat_wave_total_length: ["Durée totale des vagues de chaleur",
                                 "Durée",
                                 "jours"],
    idx_hot_spell_frequency:    ["Nombre de périodes chaudes",
                                 "Nbr. périodes",
                                 "périodes"],
    idx_hot_spell_max_length:   ["Durée maximale des périodes chaudes",
                                 "Durée",
                                 "jours"],
    idx_tgg:                    ["Température moyenne calculée à partir de Tmin et Tmax",
                                 "Température",
                                 "°C"],
    idx_tng:                    ["Nbr mois frais (moyenne mensuelle de Tmin < X°C)",
                                 "Nbr. mois",
                                 "mois"],
    idx_tnx:                    ["Valeur maximale de Tmin",
                                 "Température",
                                 "°C"],
    idx_txg:                    ["Valeur moyenne de Tmax",
                                 "Température",
                                 "°C"],
    idx_tng_months_below:       ["Nombre de mois frais",
                                 "Nbr. mois",
                                 ""],
    idx_tx_days_above:          ["Nombre de jours chauds (Tmax > X°C)",
                                 "Nbr. jours",
                                 "jours"],
    idx_tn_days_below:          ["Nombre de jours frais (Tmin < X°C)",
                                 "Nbr. jours",
                                 "jours"],
    idx_tropical_nights:        ["Nombre de nuits chaudes (Tmin > X°C)",
                                 "Nbr. jours",
                                 "jours"],
    idx_wsdi:                   ["Indice de durée des périodes chaudes (Tmax ≥ X; Y jours consécutifs)",
                                 "Indice",
                                 ""],
    idx_rx1day:                 ["Cumul de précipitations (1 jour)",
                                 "Cumul",
                                 "mm"],
    idx_rx5day:                 ["Cumul de précipitations (5 jours)",
                                 "Cumul",
                                 "mm"],
    idx_cdd:                    ["Nombre de jours secs consécutifs (P < X mm)",
                                 "Nbr. jours",
                                 "jours"],
    idx_cwd:                    ["Nombre de jours pluvieux consécutifs (P ≥ X mm)",
                                 "Nbr. jours",
                                 "jours"],
    idx_dry_days:               ["Nombre de jours secs (P < X mm)",
                                 "Nbr. jours",
                                 "jours"],
    idx_wet_days:               ["Nombre de jours pluvieux (P ≥ X mm)",
                                 "Nbr. jours",
                                 "jours"],
    idx_prcptot:                ["Cumul de précipitation (entre les jours X et Y)",
                                 "Cumul",
                                 "mm"],
    idx_r10mm:                  ["Nombre de jours avec P ≥ 10 mm",
                                 "Nbr. jours",
                                 "jours"],
    idx_r20mm:                  ["Nombre de jours avec P ≥ 20 mm",
                                 "Nbr. jours",
                                 "jours"],
    idx_rnnmm:                  ["Nombre de jours avec P ≥ X mm",
                                 "Nbr. jours",
                                 "jours"],
    idx_sdii:                   ["Intensité moyenne des précipitations",
                                 "Intensité",
                                 "mm/day"],
    idx_rain_season_start:      ["Début de la saison de pluie",
                                 "Jour",
                                 ""],
    idx_rain_season_end:        ["Fin de la saison de pluie",
                                 "Jour",
                                 ""],
    idx_rain_season_length:     ["Durée de la saison de pluie",
                                 "Nbr. Jours",
                                 "jours"],
    idx_rain_season_prcptot:    ["Cumul de précipitation pendant la saison de pluie",
                                 "Cumul",
                                 "mm"],
    idx_dry_spell_total_length: ["Durée totale des périodes sèches (P < X mm/jour; Y jours consécutifs)",
                                 "Nbr. jours",
                                 "jours"],
    idx_wg_days_above:          ["Nombre de jours avec vent fort (Vmoy ≥ X km/h)",
                                 "Nbr. jours",
                                 "jours"],
    idx_wx_days_above:          ["Nombre de jours avec vent fort directionel (Vmax ≥ X km/h; direction de Y±Z°)",
                                 "Nbr. jours",
                                 "jours"],
    idx_drought_code:           ["Code de sécheresse",
                                 "Code",
                                 ""]
}

class VarIdx(object_def.Obj):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object VarIdx.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Contructor.
    def __init__(self, code):
        super().__init__(code)
    
    def get_name(
        self
    ) -> str:

        """
        Extract name.

        Returns
        -------
        str
            Name.
        """

        pos = self.code.rfind("_")
        if pos >= 0:
            tokens = self.code.split("_")
            if tokens[len(tokens) - 1].isdigit():
                return self.code[0:pos]

        return self.code
    
    def get_desc(
        self,
    ) -> str:
    
        """
        Get description.

        Returns
        -------
        str
            Description.
        """

        return code_props[self.get_name()][0]
    
    def get_unit(
        self,
    ) -> str:
    
        """
        Get unit.

        Returns
        -------
        str
            Unit.
        """

        return code_props[self.get_name()][2]
    
    
    def get_label(
        self
    ) -> str:

        """
        Combine description and unit.

        Returns
        -------
        str
            Combine description and unit.
        """

        desc = self.get_desc()
        unit = self.get_unit()
        if (unit not in ["", "1"]) and (unit not in desc):
            unit = " (" + unit + ")"
        
        return desc + unit
    
    def is_var(
        self
    ) -> bool:
        
        """
        Determine if the instance is a variable.
        """
        
        return self.get_name() in vars

    def copy(
        self
    ):
        
        """
        Copy item.
        """
        
        return VarIdx(self.code)

    
class VarIdxs(object_def.Objs):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object VarIdxs.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # List of instances.
    items = []

    # Constructors.
    def __init__(self, *args):
        
        if len(args) == 0:
            self.items = []
        
        else:
            self.load(args)

    def load(self, args) -> List[str]:

        """
        Load items.

        Parameters
        ----------
        args :
            args[0] : str
                View = {"ts", "tbl", "map"}
        """

        view = args[0]
        
        code_l = []

        if view in [view_def.mode_ts, view_def.mode_tbl]:
            p = cf.d_data + "<view>/*.csv"
            p = p.replace("<view>", view)
            f_l = list(glob.glob(p))
            for f in f_l:
                code_l.append(os.path.basename(f).replace(".csv", ""))
            code_l.sort()

        else:
            p = cf.d_data + "<view>/"
            p = p.replace("<view>", view)
            code_l = utils.list_dir(p)
        
        # Create items.
        self.items = []
        for code in code_l:
            self.items.append(VarIdx(code))

    def get_code(
        self,
        desc: str
    ) -> str:

        """
        Get code.

        Paramters
        ---------
        desc : str
            Description.

        Returns
        -------
        str
            Code.
        """    

        for item in self.items:
            if item.get_desc() == desc:
                return item.code

        return ""


    def get_desc(
        self,
        code: str
    ) -> str:

        """
        Get description.

        Paramters
        ---------
        code : str
            Code.

        Returns
        -------
        str
            Description.
        """    

        for item in self.items:
            if item.get_code() == code:
                return item.desc  

        return ""

    def get_code_l(
        self
    ) -> List[str]:
    
        """
        Get codes.
    
        Returns
        -------
        List[str]
            Codes.
        """
    
        code_l = []
    
        for item in self.items:
            code_l.append(item.get_code())
    
        return code_l
    
    def get_desc_l(
        self
    ) -> List[str]:
    
        """
        Get descriptions.
    
        Returns
        -------
        List[str]
            Descriptions.
        """
    
        desc_l = []
    
        for item in self.items:
            desc_l.append(item.get_desc())
    
        return desc_l
