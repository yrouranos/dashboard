# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Context.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import ast
import configparser
import os
import pandas as pd
from typing import List, Type, Union

# Dasboard libraries.
import def_object
from def_constant import const as c

"""
------------------------------------------------------------------------------------------------------------------------
File dependencies:

dash_test, dash, dash_ipynb
|
+- def_constant, def_context, def_delta, def_hor, def_lib, def_project, def_rcp, def_sim, def_stat, def_varidx, def_view
|
+- dash_plot
|  |
|  +- def_context, dash_utils
|  |  +- def_constant, def_object
|  |
|  +- def_stat, def_rcp
|  |  +- def_constant, def_context, def_object
|  |
|  +- def_sim: 
|     +- def_constant, def_context, def_object, def_rcp
|
+- dash_utils

------------------------------------------------------------------------------------------------------------------------
Class hierarchy:

+- Context
|  |
|  +- Projects -> Project
|  +- Project
|  +- Views -> View
|  +- View 
|  +- Libs -> Lib
|  +- Lib
|  +- Deltas -> Delta
|  +- Delta
|  +- VarIdxs -> VarIdx
|  +- VarIdx
|  +- Hors -> Hor
|  +- Hor
|  |
|  +- RCPs --+
|  +- RCP  <-+
|  |
|  +- Sims --+
|  +- Sim  <-+
|  |  +- RCP
|  |
|  +- Stats -> Stat
|  +- Stat
|
+- Constant

------------------------------------------------------------------------------------------------------------------------
"""


class Context(def_object.Obj):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object context.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Base directory of data (dashboard only).
    _d_data = "./data/"

    # Path of .geogjson file defining region boundaries.
    _p_bounds = "boundaries.geojson"

    """
    Color maps apply to categories of variables and indices.
    
    Variable, category         |   Variable |      Index
    ---------------------------+------------+-----------
    temperature, high values   | temp_var_1 | temp_idx_1
    temperature, low values    |          - | temp_idx_2
    ---------------------------+------------+-----------
    precipitation, high values | prec_var_1 | prec_idx_1
    precipitation, low values  |          - | prec_idx_2
    precipitation, dates       |          - | prec_idx_3
    ---------------------------+------------+-----------
    evaporation, high values   | evap_var_1 | evap_idx_1
    evaporation, low values    |          - | evap_idx_2
    evaporation, dates         |          - | evap_idx_3
    ---------------------------+------------+-----------
    wind                       | wind_var_1 | wind_idx_1

    Notes:
    - The 1st scheme is for absolute values.
    - The 2nd scheme is divergent and his made to represent delta values when both negative and positive values are
      present.
      It combines the 3rd and 4th schemes.
    - The 3rd scheme is for negative-only delta values.
    - The 4th scheme is for positive-only delta values.
    """

    opt_map_col_temp_var   = ["viridis", "RdBu_r", "Blues_r", "Reds"]
    opt_map_col_temp_idx_1 = opt_map_col_temp_var
    opt_map_col_temp_idx_2 = ["plasma_r", "RdBu", "Reds_r", "Blues"]
    opt_map_col_prec_var   = ["Blues", "BrWhGr", "Browns_r", "Greens"]
    opt_map_col_prec_idx_1 = opt_map_col_prec_var
    opt_map_col_prec_idx_2 = ["Oranges", "GrWhBr", "Greens_r", "Browns"]
    opt_map_col_prec_idx_3 = ["viridis", "RdBu_r", "Blues_r", "Reds"]
    opt_map_col_evap_var   = ["Browns", "GrWhBr", "Blues_r", "Greens_r"]
    opt_map_col_evap_idx_1 = opt_map_col_evap_var
    opt_map_col_evap_idx_2 = ["Greens", "BrWhGr", "Oranges_r", "Browns_r"]
    opt_map_col_evap_idx_3 = ["Blues", "RdBu", "viridis_r", "Reds_r"]
    opt_map_col_wind_var   = ["None", "RdBu_r", "Blues_r", "Reds"]
    opt_map_col_wind_idx_1 = ["Reds", "RdBu_r", "Blues_r", "Reds"]
    opt_map_col_default    = ["viridis", "RdBu_r", "Blues_r", "Reds"]

    def __init__(
        self,
        code: str
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Context, self).__init__(code, code)

        # Software ---------------------------------

        self.version = ""

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

        # Deltas.
        self.delta = None
        self.deltas = None

        # Variable or index (selected and all).
        self.varidx = None
        self.varidxs = None

        # Horizons (selected and all).
        self.hor = None
        self.hors = None

        # Emission scenarios (selected and all).
        self.rcp = None
        self.rcps = None

        # Simulations (selected and all).
        self.sim = None
        self.sims = None

        # Statistics (selected and all).
        self.stat = None
        self.stats = None

        # Configuration file -------------------

        # Codes.
        self.idx_codes = []

        # Parameters.
        self.idx_params = []

        # Reference period.
        self.per_ref = []

        # Dashboard ----------------------------

        # Background color of sidebar.
        self.col_sb_fill = "WhiteSmoke"

        # Results ------------------------------

        # Enable/disable the selection of a plotting library.
        self.opt_lib = False

        # Resolution.
        self.dpi = 600

        # Centiles required to produce a cluster scatter plot (if a single variable is selected).
        self.opt_cluster_centiles = [10, 50, 90]

        # Color scale (cluster plot).
        self.opt_cluster_col = "Dark2"

        # Centiles for which a map is required.
        self.opt_map_centiles = [10, 90]

        # Discrete vs. continuous colors scales (maps).
        self.opt_map_discrete = True

        # Map locations (pd.DataFrame).
        self.opt_map_locations = None

        # Centiles required to generate a statistical table.
        self.opt_tbl_centiles = [0, 1, 10, 50, 90, 99, 100]

        # Centiles for which a time series is required.
        self.opt_ts_centiles = [10, 90]

    def load(
        self,
        fn_ini: str = "config.ini"
    ):

        """
        ----------------------------------------
        Load parameters.

        There are two types of configurations files: global to the portal and project-specific.

        Parameters
        ----------
        fn_ini : str
            Name of INI file.
        ----------------------------------------
        """

        # Load global configuration file.

        p_ini_global = cntx.d_data + fn_ini

        if os.path.exists(p_ini_global):

            # Read file.
            config = configparser.ConfigParser()
            config.read(p_ini_global)

            # Loop through sections.
            for section in config.sections():

                # Loop through keys.
                for key in config[section]:

                    # Extract value.
                    value = config[section][key]

                    if key == "version":
                        self.version = value

                    elif (key == "projects") and (cntx.projects is not None):
                        project_l = str_to_arr_2d(value, float)
                        for i in range(len(cntx.projects.items)):
                            for j in range(len(project_l)):
                                if cntx.projects.items[i].code == project_l[j][0]:
                                    cntx.projects.items[i].desc = project_l[j][1]
                                    break

        # Load project-specific configuration file.
        project_code = self.project.code if self.project is not None else ""
        if project_code == "":
            return
        p_ini_project = cntx.d_data + project_code + "/" + fn_ini

        if os.path.exists(p_ini_project):

            # Read file.
            config = configparser.ConfigParser()
            config.read(p_ini_project)

            # Loop through sections.
            for section in config.sections():

                # Loop through keys.
                for key in config[section]:

                    # Extract value.
                    value = config[section][key]

                    if key == "idx_codes":
                        self.idx_codes = str_to_arr_1d(value, str)

                    elif key == "idx_params":
                        idx_params = str_to_arr_2d(value, float)
                        self.idx_params = []
                        for i in range(len(self.idx_codes)):
                            if "r10mm" in self.idx_codes[i]:
                                self.idx_params.append([10])
                            elif "r20mm" in self.idx_codes[i]:
                                self.idx_params.append([20])
                            else:
                                self.idx_params.append(idx_params[i])

                    elif key == "per_ref":
                        self.per_ref = str_to_arr_1d(value, int)

                    elif key == "opt_lib":
                        self.opt_lib = ast.literal_eval(value)

                    elif key == "opt_map_centiles":
                        opt_map_centiles = str_to_arr_1d(value, int)
                        if str(opt_map_centiles).replace("['']", "") == "":
                            self.opt_map_centiles = opt_map_centiles
                            self.opt_map_centiles.sort()

                    elif key == "opt_map_locations":
                        self.opt_map_locations =\
                            pd.DataFrame(str_to_arr_2d(value, float), columns=["longitude", "latitude", "desc"])

                    elif key == "opt_tbl_centiles":
                        opt_tbl_centiles = str_to_arr_1d(value, int)
                        if str(opt_tbl_centiles).replace("['']", "") != "":
                            self.opt_tbl_centiles = opt_tbl_centiles
                            self.opt_tbl_centiles.sort()

                    elif key == "opt_ts_centiles":
                        opt_ts_centiles = str_to_arr_1d(value, int)
                        if str(opt_ts_centiles).replace("['']", "") == "":
                            self.opt_ts_centiles = opt_ts_centiles
                            self.opt_ts_centiles.sort()

                    elif key == "opt_cluster_centiles":
                        opt_cluster_centiles = str_to_arr_1d(value, int)
                        if str(opt_cluster_centiles).replace("['']", "") == "":
                            self.opt_cluster_centiles = opt_cluster_centiles
                            self.opt_cluster_centiles.sort()

    def idx_params_from_code(
        self,
        idx_code: str
    ) -> List[any]:

        """
        ----------------------------------------
        Get the parameters associated with an index.

        Parameters
        ----------
        idx_code: str
            Index code.

        Returns
        -------
        List[any]
            Parameters associated with an index code.
        ----------------------------------------
        """

        # Loop through index codes.
        for i in range(len(self.idx_codes)):
            if idx_code in self.idx_codes[i]:
                return self.idx_params[i]

        return []

    @property
    def d_data(
        self
    ) -> str:

        """
        ----------------------------------------
        Get the base directory of data.

        Returns
        -------
        str
            Base directory of data.
        ----------------------------------------
        """

        return self._d_data

    @property
    def d_project(
        self
    ) -> str:

        """
        ----------------------------------------
        Get the base directory of project.

        Returns
        -------
        str
            Base directory of project.
        ----------------------------------------
        """

        d = self._d_data + "<project_code>/"
        d = d.replace("<project_code>/", "" if cntx.project is None else cntx.project.code + "/")

        return d

    @property
    def p_logo(
        self
    ) -> str:

        """
        ----------------------------------------
        Get path of logo.

        Returns
        -------
        str
            Path of logo.
        ----------------------------------------
        """

        return self._d_data + "ouranos.png"

    @property
    def p_bounds(
        self
    ) -> str:

        """
        --------------------------------------------------------------------------------------------------------------------
        Get the path of the .geojson file defining region boundaries.

        Returns
        -------
        str
            Path of the .geojson file defining region boundaries.
        --------------------------------------------------------------------------------------------------------------------
        """

        if self.code in [c.platform_streamlit, c.platform_jupyter]:
            p = cntx.d_project + "<view_code>/" + self._p_bounds
            p = p.replace("<view_code>", cntx.view.code)
        else:
            p = self._p_bounds

        return p

    @p_bounds.setter
    def p_bounds(
        self,
        p_bounds: str
    ):

        """
        ----------------------------------------
        Set the path of the .geojson file defining region boundaries.

        Parameters
        ----------
        p_bounds: str
            Path of the .geojson file defining region boundaries.
        ----------------------------------------
        """

        self._p_bounds = p_bounds

    @property
    def per_ref_str(
        self
    ) -> str:

        """
        ----------------------------------------
        Get the reference period as a string.

        Returns
        -------
        str
            Reference period as a string (ex: "1981-2010").
        ----------------------------------------
        """

        per_ref = ""

        if len(self.per_ref) == 2:
            per_ref = str(self.per_ref[0]) + "-" + str(self.per_ref[1])

        return per_ref


def replace_right(
    s: str,
    str_a: str,
    str_b: str,
    n_occurrence: int
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Replace the right-most instance of a string 'str_a' with a string 'str_b' within a string 's'.

    Parameters
    ----------
    s : str
        String that will be altered.
    str_a : str
        String to be replaced in 's'.
    str_b : str
        String to replace with in 's'.
    n_occurrence : int
        Number of occurences.

    Returns
    -------
    str
        Altered string.
    --------------------------------------------------------------------------------------------------------------------
    """

    li = s.rsplit(str_a, n_occurrence)

    return str_b.join(li)


def str_to_arr_1d(
    vals: str,
    to_type: Union[Type[bool], Type[int], Type[float], Type[str]]
) -> List[Union[Type[bool], Type[int], Type[float], Type[str]]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Convert values to a 1D-array of the selected type.

    Parameters
    ----------
    vals : str
        Values.
    to_type: Union[Type[bool], Type[int], Type[float], Type[str]]
        Type to convert to.

    Returns
    -------
    List[Union[Type[bool], Type[int], Type[float], Type[str]]]
        1D-array of the selected type.
    --------------------------------------------------------------------------------------------------------------------
    """

    if to_type == str:
        vals = ast.literal_eval(vals)
    elif to_type == bool:
        vals = str(replace_right(vals.replace("[", "", 1), "]", "", 1)).split(",")
        vals = [True if val == 'True' else False for val in vals]
    else:
        vals = str(replace_right(vals.replace("[", "", 1), "]", "", 1)).lstrip().rstrip().split(",")
        for i_val in range(len(vals)):
            try:
                vals[i_val] = int(vals[i_val])
            except ValueError:
                try:
                    vals[i_val] = float(vals[i_val])
                except ValueError:
                    pass

    return vals


def str_to_arr_2d(
    vals: str,
    to_type: Union[Type[bool], Type[int], Type[float], Type[str]]
) -> List[List[Union[Type[bool], Type[int], Type[float], Type[str]]]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Convert values to a 2D-array of the selected type.

    Parameters
    ----------
    vals : str
        Values.
    to_type: Union[Type[bool], Type[int], Type[float], Type[str]]
        Type to convert to.

    Returns
    -------
    List[List[Union[Type[bool], Type[int], Type[float], Type[str]]]]
        2D-array of the selected type.
    --------------------------------------------------------------------------------------------------------------------
    """

    vals_new = []
    vals = vals[1:(len(vals) - 1)].split("],")
    for i_val in range(len(vals)):
        val_i = str_to_arr_1d(vals[i_val], to_type)
        vals_new.append(val_i)

    return vals_new


# Configuration instance.
cntx = Context("")
