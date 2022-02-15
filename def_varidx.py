# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: RCP and RCPs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
import os
from typing import List, Union

# Dashboard libraries.
import def_object
from def_constant import const as c
from def_context import cntx


def code_props(
) -> dict:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and properties.

    Returns
    -------
    dict
        Dictionary of codes and properties.
        Cell 1: Long description
        Cell 2: Short description (for y-label).
        Cell 3: Units.
        Cell 4: Precision (number of decimal places to show).
    --------------------------------------------------------------------------------------------------------------------
    """

    return {

        # Variables (CORDEX):
        c.v_tas:                    ["Température moyenne",              "Température",           "°C",    1],
        c.v_tasmin:                 ["Température minimale journalière", "Température",           "°C",    1],
        c.v_tasmax:                 ["Température maximale journalière", "Température",           "°C",    1],
        c.v_uas:                    ["Vitesse du vent (dir. est)",       "Vitesse",               "km/h",  0],
        c.v_vas:                    ["Vitesse du vent (dir. nord)",      "Vitesse",               "km/h",  0],
        c.v_sfcwindmax:             ["Vitesse du vent",                  "Vitesse",               "km/h",  0],
        c.v_ps:                     ["Pression barométrique",            "Pression barométrique", "Pa",    0],
        c.v_rsds:                   ["Radiation solaire",                "Radiation solaire",     "Pa",    0],
        c.v_pr:                     ["Précipitation",                    "Cumul",                 "mm",    0],
        c.v_evspsbl:                ["Évapotranspiration",               "Cumul",                 "mm",    0],
        c.v_evspsblpot:             ["Évapotranspiration potentielle",   "Cumul",                 "mm",    0],
        c.v_huss:                   ["Humidité spécifique",              "Humidité spécifique",   "",      2],
        c.v_clt:                    ["Couvert nuageux",                  "Couvert nuageux",       "%",     1],

        # Variables (ERA5 and ERA5-Land):
        c.v_era5_d2m:               ["Point de rosée",                   "Point de rosée",        "",      1],
        c.v_era5_t2m:               ["Température moyenne",              "Température",           "°C",    1],
        c.v_era5_t2mmin:            ["Température minimale journalière", "Température",           "°C",    1],
        c.v_era5_t2mmax:            ["Température maximale journalière", "Température",           "°C",    1],
        c.v_era5_sp:                ["Pression barométrique",            "Pression barométrique", "Pa",    0],
        c.v_era5_tp:                ["Précipitation",                    "Cumul",                 "mm",    0],
        c.v_era5_u10:               ["Vitesse du vent (dir. est)",       "Vitesse",               "km/h",  0],
        c.v_era5_u10min:            ["Vitesse du vent min. (dir. est)",  "Vitesse",               "km/h",  0],
        c.v_era5_u10max:            ["Vitesse du vent max. (dir. est)",  "Vitesse",               "km/h",  0],
        c.v_era5_v10:               ["Vitesse du vent (dir. nord)",      "Vitesse",               "km/h",  0],
        c.v_era5_v10min:            ["Vitesse du vent min. (dir. nord)", "Vitesse",               "km/h",  0],
        c.v_era5_v10max:            ["Vitesse du vent max. (dir. nord)", "Vitesse",               "km/h",  0],
        c.v_era5_uv10:              ["Vitesse du vent",                  "Vitesse",               "km/h",  0],
        c.v_era5_uv10min:           ["Vitesse du vent min.",             "Vitesse",               "km/h",  0],
        c.v_era5_uv10max:           ["Vitesse du vent max.",             "Vitesse",               "km/h",  0],
        c.v_era5_ssrd:              ["Radiation solaire",                "Radiation solaire",     "Pa",    0],
        c.v_era5_e:                 ["Évaporation",                      "Cumul",                 "mm",    0],
        c.v_era5_pev:               ["Évapotranspiration potentielle",   "Cumul",                 "mm",    0],
        c.v_era5_sh:                ["Humidité spécifique",              "Humidité spécifique",   "",      2],

        # Variables (ENACTS):
        c.v_enacts_tmin:            ["Température minimale journalière", "Température",           "°C",    1],
        c.v_enacts_tmax:            ["Température maximale journalière", "Température",           "°C",    1],
        c.v_enacts_rr:              ["Précipitation",                    "Cumul",                 "mm",    0],
        c.v_enacts_pet:             ["Évapotranspiration potentielle",   "Cumul",                 "mm",    0],

        # Indices:
        c.i_etr:                    ["Écart extrême de température",     "Température",           "°C",    1],
        c.i_tx90p:                  ["Nombre de jours chauds (Tmax > 90e percentile)", "Nbr. jours", "jours", 0],
        c.i_heat_wave_max_length:   ["Durée maximale des vagues de chaleur", "Durée", "jours", 0],
        c.i_heat_wave_total_length: ["Durée totale des vagues de chaleur", "Durée", "jours", 0],
        c.i_hot_spell_frequency:    ["Nombre de périodes chaudes", "Nbr. périodes", "périodes", 0],
        c.i_hot_spell_max_length:   ["Durée maximale des périodes chaudes", "Durée", "jours", 0],
        c.i_tgg:                    ["Température moyenne (à partir de Tmin et Tmax)", "Température", "°C", 1],
        c.i_tng:                    ["Nbr mois frais (μ_mois(Tmin) < <A>°C)", "Nbr. mois", "mois", 1],
        c.i_tnx:                    ["Valeur maximale de Tmin", "Température", "°C", 1],
        c.i_txg:                    ["Valeur moyenne de Tmax", "Température", "°C", 1],
        c.i_txx:                    ["Température maximale", "Température", "°C", 1],
        c.i_tng_months_below:       ["Nombre de mois frais", "Nbr. mois", "", 1],
        c.i_tx_days_above:          ["Nombre de jours chauds (Tmax > <A>°C)", "Nbr. jours", "jours", 0],
        c.i_tn_days_below:          ["Nombre de jours frais (Tmin < <A>°C)", "Nbr. jours", "jours", 0],
        c.i_tropical_nights:        ["Nombre de nuits chaudes (Tmin > <A>°C)", "Nbr. jours", "jours", 0],
        c.i_wsdi:                   ["Indice de durée des périodes chaudes (Tmax ≥ <A>; <B> jours consécutifs)",
                                     "Indice", "", 0],
        c.i_rx1day:                 ["Cumul de précipitations (1 jour)", "Cumul", "mm", 0],
        c.i_rx5day:                 ["Cumul de précipitations (5 jours)", "Cumul", "mm", 0],
        c.i_cdd:                    ["Nombre de jours secs consécutifs (P < <A> mm)", "Nbr. jours", "jours", 0],
        c.i_cwd:                    ["Nombre de jours pluvieux consécutifs (P ≥ <A> mm)", "Nbr. jours", "jours", 0],
        c.i_dry_days:               ["Nombre de jours secs (P < <A> mm)", "Nbr. jours", "jours", 0],
        c.i_wet_days:               ["Nombre de jours pluvieux (P ≥ <A> mm)", "Nbr. jours", "jours", 0],
        c.i_prcptot:                ["Cumul de précipitation (entre les jours <A> et <B>)", "Cumul", "mm", 0],
        c.i_r10mm:                  ["Nombre de jours avec P ≥ 10 mm", "Nbr. jours", "jours", 0],
        c.i_r20mm:                  ["Nombre de jours avec P ≥ 20 mm", "Nbr. jours", "jours", 0],
        c.i_rnnmm:                  ["Nombre de jours avec P ≥ <A> mm", "Nbr. jours", "jours", 0],
        c.i_sdii:                   ["Intensité moyenne des précipitations", "Intensité", "mm/day", 0],
        c.i_rain_season_start:      ["Début de la saison de pluie", "Jour", "", 0],
        c.i_rain_season_end:        ["Fin de la saison de pluie", "Jour", "", 0],
        c.i_rain_season_length:     ["Durée de la saison de pluie", "Nbr. Jours", "jours", 0],
        c.i_rain_season_prcptot:    ["Cumul de précipitation pendant la saison de pluie", "Cumul", "mm", 0],
        c.i_dry_spell_total_length: ["Durée totale des périodes sèches (P < <A> mm/jour; <B> jours consécutifs)",
                                     "Nbr. jours", "jours", 0],
        c.i_wg_days_above:          ["Nombre de jours avec vent fort (Vmoy ≥ <A> km/h)", "Nbr. jours", "jours", 0],
        c.i_wx_days_above:          ["Nombre de jours avec vent fort directionel (Vmax ≥ <A> km/h; de <B>±<C>°)",
                                     "Nbr. jours", "jours", 0],
        c.i_drought_code:           ["Code de sécheresse", "Code", "", 0]
    }


class VarIdx(def_object.Obj):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object VarIdx.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Parameters.
    _params = []

    def __init__(
        self,
        code: str
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        vi_name = extract_vi_name(code)
        if (code == "") or (vi_name not in dict(code_props()).keys()):
            desc = ""
        else:
            desc = dict(code_props())[vi_name][0]
        super(VarIdx, self).__init__(code=code, desc=desc)

    @property
    def name(
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

    @property
    def desc(
        self,
    ) -> str:

        """
        ----------------------------------------
        Get title.

        Returns
        -------
        str
            Title.
        ----------------------------------------
        """

        desc = dict(code_props())[self.name][0]

        # Assign first parameter.
        if self.name in [c.i_tng, c.i_tx_days_above, c.i_tn_days_below, c.i_tropical_nights, c.i_wsdi, c.i_cdd,
                         c.i_cwd, c.i_dry_days, c.i_wet_days, c.i_prcptot, c.i_rnnmm, c.i_dry_spell_total_length,
                         c.i_wg_days_above, c.i_wx_days_above]:
            desc = desc.replace("<A>", str(self.params[0]))

        # Assign 2nd parameter.
        if self.name in [c.i_wsdi, c.i_prcptot, c.i_dry_spell_total_length, c.i_wx_days_above]:
            desc = desc.replace("<B>", str(self.params[1]) if len(self.params) >= 2 else "1")

        # Assign 3rd parameter.
        if self.name in [c.i_wx_days_above, c.i_prcptot]:
            desc = desc.replace("<C>", str(self.params[2]) if len(self.params) >= 3 else "365")

        return desc

    @property
    def label(
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

        label = dict(code_props())[extract_vi_name(self.code)][1]

        unit = str(self.unit)
        if (unit not in ["", "1"]) and (unit not in label):
            label += " (" + unit + ")"

        return label

    @property
    def unit(
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

        return dict(code_props())[extract_vi_name(self.code)][2]

    @property
    def precision(
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

        return dict(code_props())[extract_vi_name(self.code)][3]

    @property
    def is_var(
        self
    ) -> bool:
        
        """
        ----------------------------------------
        Determine if the instance is a variable.
        ----------------------------------------
        """

        return self.ens in [c.ens_cordex, c.ens_era5, c.ens_era5_land, c.ens_merra2, c.ens_enacts]

    @property
    def is_summable(
        self
    ) -> bool:

        """
        ----------------------------------------
        Determine if the variable is summable.

        An summable variable can have its values summed up at a given frequency (ex: precipitation).
        ----------------------------------------
        """

        summable_variables = [c.v_pr, c.v_evspsbl, c.v_evspsblpot,
                              c.v_era5_tp, c.v_era5_e, c.v_era5_pev,
                              c.v_enacts_rr, c.v_enacts_pet]

        return self.name in summable_variables

    @property
    def is_group(
            self
    ) -> bool:

        """
        ----------------------------------------
        Determine if the instance is a group of indices.
        ----------------------------------------
        """

        return group(self.code) == self.code

    @property
    def ens(
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
        if self.name in c.variables:
            ens = c.ens_cordex

        # ERA5 and ERA5-Land.
        elif self.name in c.variables_era5:
            ens = c.ens_era5

        # ENACTS.
        elif self.name in c.variables_enacts:
            ens = c.ens_enacts

        return ens

    @property
    def params(
        self
    ) -> List[any]:

        """
        ----------------------------------------
        Get parameters.

        Returns
        -------
        List[any]
            Parameters.
        ----------------------------------------
        """

        # By default, use the available parameters.
        params = self._params

        # If no parameters are set, use those in the configuration file.
        if len(params) == 0:
            params = cntx.idx_params_from_code(self.code)

        return params

    @params.setter
    def params(
        self,
        params: List[any]
    ):

        """
        ----------------------------------------
        Set parameters.

        Parameters
        ----------
        params: List[any]
            Parameters.
        ----------------------------------------
        """

        self._params = params

    def convert_name(
        self,
        ens: str
    ) -> Union[any, str]:

        """
        ----------------------------------------
        Convert from CORDEX variable name to the equivalent variable name in another set (ERA5*, ENACTS)
        (or the opposite).

        Parameters
        ----------
        ens: str
            Ensemble.
        ----------------------------------------
        """

        # Equivalences.
        equi = [[c.v_tas,        c.v_era5_t2m,     ""],
                [c.v_tasmin,     c.v_era5_t2mmin,  c.v_enacts_tmin],
                [c.v_tasmax,     c.v_era5_t2mmax,  c.v_enacts_tmax],
                [c.v_pr,         c.v_era5_tp,      c.v_enacts_rr],
                [c.v_uas,        c.v_era5_u10,     ""],
                [c.v_vas,        c.v_era5_v10,     ""],
                [c.v_sfcwindmax, c.v_era5_uv10max, ""],
                [c.v_ps,         c.v_era5_sp,      ""],
                [c.v_rsds,       c.v_era5_ssrd,    ""],
                [c.v_evspsbl,    c.v_era5_e,       ""],
                [c.v_evspsblpot, c.v_era5_pev,     c.v_enacts_pet],
                [c.v_huss,       c.v_era5_sh,      ""]]

        # Loop through equivalences.
        for i in range(len(equi)):

            # Verify if there is a match.
            if self.name in equi[i]:
                if self.ens == c.ens_cordex:
                    if ens in [c.ens_era5, c.ens_era5_land]:
                        return equi[i][1]
                    elif ens == c.ens_enacts:
                        return equi[i][2]
                else:
                    return equi[i][0]

        return None

    def equi_path(
        self,
        p: str,
        vi_code_b: str,
        stn: str,
        rcp: str
    ) -> str:

        """
        ----------------------------------------
        Determine the equivalent path for another variable or index.

        Parameters
        ----------
        p: str
            Path associated with the current instance.
        vi_code_b: str
            Name of climate variable or index to replace with.
        stn: str
            Station name.
        rcp: str
            Emission scenario.
        ----------------------------------------
        """

        # Determine if we have variables or indices.
        vi_code_a = self.code
        varidx_b = VarIdx(vi_code_b)
        a_is_var = self.name in cntx.vars.code_l
        b_is_var = varidx_b.name in cntx.vars.code_l
        fn = os.path.basename(p)

        # No conversion required.
        if vi_code_a != vi_code_b:

            # Variable->Variable or Index->Index.
            if (a_is_var and b_is_var) or (not a_is_var and not b_is_var):
                p = p.replace(self.name, varidx_b.name)

            # Variable -> Index (or the opposite)
            else:

                # Variable -> Index.
                if a_is_var and not b_is_var:
                    p = cntx.d_idx(vi_code_b)

                # Index -> Variable.
                else:
                    if rcp == c.ref:
                        p = cntx.d_stn(vi_code_b)
                    else:
                        p = cntx.d_scen(c.cat_qqmap, vi_code_b)
                # Both.
                if rcp == c.ref:
                    p += varidx_b.name + "_" + c.ref + c.f_ext_nc
                else:
                    p += fn.replace(self.name + "_", varidx_b.name + "_")

        return p


class VarIdxs(def_object.Objs):
    
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
            if args[0] == "*":
                self.load()
            else:
                self.add(args[0])

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """
        
        code_l = []

        # Codes.
        view_code = cntx.view.code if cntx.view is not None else ""
        if view_code == c.view_cluster:
            view_code = c.view_ts

        # The items are extracted from directory names.
        # ~/<project_code>/<view_code>/*
        if view_code in [c.view_tbl]:
            p = cntx.d_project + "<view_code>/*.csv"
            p = p.replace("<view_code>/", view_code.split("-")[0] + "*/")
            for p_i in list(glob.glob(p)):
                code = os.path.basename(p_i).replace(".csv", "")
                if code not in code_l:
                    code_l.append(code)

        # The items are extracted from directory names.
        # ~/<project_code>/<view_code>/<varidx_code>/*
        elif view_code in [c.view_ts, c.view_map, c.view_cycle, c.view_ts_bias, c.view_cluster]:
            p = cntx.d_project + "<view_code>*/*"
            p = p.replace("<view_code>", view_code)
            for p_i in list(glob.glob(p)):
                code = os.path.basename(p_i)
                if (code not in code_l) and (os.path.isdir(p_i)):
                    code_l.append(code)
        code_l.sort()

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], VarIdx],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item : Union[str, List[str], VarIdx]
            Item (code, list of codes or instance of VarIdx).
        inplace : bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, VarIdx):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(VarIdx(code_l[i]))

        return super(VarIdxs, self).add(items, inplace)

    @property
    def desc_l(
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

        desc_l = []

        for item in self._items:
            desc_l.append(item.desc)

        return desc_l

    @property
    def name_l(
        self
    ) -> List[str]:

        """
        ----------------------------------------
        Get a list of names.

        Returns
        -------
        List[str]
            Names.
        ----------------------------------------
        """

        name_l = []

        for item in self._items:
            name_l.append(item.name)

        return name_l


def extract_vi_name(
    vi_code: str
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Extract name.

    Parameters
    ----------
    vi_code: str
        Variable or index code.

    Returns
    -------
    str
        Variable or index name.
    --------------------------------------------------------------------------------------------------------------------
    """

    pos = vi_code.rfind("_")
    if pos >= 0:
        tokens = vi_code.split("_")
        if tokens[len(tokens) - 1].isdigit():
            return vi_code[0:pos]

    return vi_code


def group(
    vi_code: str = ""
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the name of a group of indices.

    Parameters
    ----------
    vi_code : str, optional
        Variable or index code.

    Returns
    -------
    str
        Group name.
    --------------------------------------------------------------------------------------------------------------------
    """

    for key in list(c.i_groups.keys()):
        if vi_code in c.i_groups[key]:
            return key

    return ""


def explode_idx_l(
    idx_group_l
) -> [str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Explode a list of index names or codes, e.g. [rain_season_1, rain_season_2] into
    [rain_season_start_1, rain_season_end_1, rain_season_length_1, rain_season_prcptot_1,
     rain_season_start_2, rain_season_end_2, rain_season_length_2, rain_season_prcptot_2].

    Parameters
    ----------
    idx_group_l: [str]
        List of climate index groups.
    --------------------------------------------------------------------------------------------------------------------
    """

    idx_l_new = []

    # Loop through index names or codes.
    for i in range(len(idx_group_l)):
        idx_code = idx_group_l[i]

        # Loop through index groups.
        in_group = False
        for key in c.i_groups:

            # Explode and add to list.
            if c.i_groups[key][0] in idx_code:
                in_group = True

                # Extract instance number of index (ex: "_1").
                no = idx_code.replace(idx_code, "")

                # Loop through embedded indices.
                for k in range(len(c.i_groups[key][1])):
                    idx_l_new.append(c.i_groups[key][1][k] + no)

        if not in_group:
            idx_l_new.append(idx_code)

    return idx_l_new
