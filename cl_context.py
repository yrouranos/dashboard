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
import glob
import os
import pandas as pd
import re
from PIL import Image
from typing import List, Type, Union, Optional

# Dasboard libraries.
import cl_auth
import cl_gd
import cl_object
from cl_constant import const as c

"""
------------------------------------------------------------------------------------------------------------------------
File dependencies:

dash_test, dash, dash_ipynb
|
+- cl_constant, cl_context, cl_delta, cl_hor, cl_lib, cl_project, cl_rcp, cl_sim, cl_stat, cl_varidx, cl_view
|
+- dash_plot
|  |
|  +- cl_context, dash_utils
|  |  +- cl_constant, cl_object
|  |
|  +- cl_stat, cl_rcp
|  |  +- cl_constant, cl_context, cl_object
|  |
|  +- cl_sim: 
|     +- cl_constant, cl_context, cl_object, cl_rcp
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


class Context(cl_object.Obj):
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object context.
    --------------------------------------------------------------------------------------------------------------------
    """

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

        # Data ---------------------------------

        # Directory holding the configuration file (on local or remote drive).
        self._d_data = str(cl_auth.path("context"))
        if self._d_data == "":
            self._d_data = c.D_DATA

        # Path of logo image (within 'context' directory).
        self.p_logo = c.F_LOGO

        # Load configuration file.
        self.drive = None
        if "gd:" in self._d_data:
            self._d_data = self._d_data.replace("gd:", "")
            self.drive = cl_gd.GoogleDrive(self._d_data)

        # DataFrame of CSV and GEOJSON files (columns: gd.PROP_PATH and gd.PROP_ITEM_ID).
        self.df_files = None

        # Objects ------------------------------

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

    def load_files(
        self
    ):

        """
        ----------------------------------------
        Load files (CSV, GEOJSON).

        There is a single GEOJSON file, which explains why the search is restrained to the 'map' directory.
        ----------------------------------------
        """

        # File extensions to consider.
        f_ext_l = [c.F_EXT_CSV, c.F_EXT_GEOJSON, c.F_EXT_INI]

        # Scan directories to find all paths to CSV files.
        if (self.df_files is None) or (len(self.df_files) == 0):

            p_l, id_l = [], []

            # Global ini file.
            p = str(cl_auth.path("context"))
            if "gd:" not in p:
                p_l = list(glob.glob(p + "context/*" + c.F_EXT_INI))
                id_l = [""]
            else:
                df_files = cl_gd.GoogleDrive(p.replace("gd:", "")).glob(pattern=("*" + c.F_EXT_INI))
                p_l = list(df_files[cl_gd.PROP_PATH])
                p_l = ["context/" + p for p in p_l]
                id_l = id_l + list(df_files[cl_gd.PROP_ITEM_ID])

            # Loop through projects.
            for project in self.projects.items:
                p_base = str(cl_auth.path(project.code))

                # Loop through files extensions.
                for f_ext in f_ext_l:

                    # Local path.
                    if "gd:" not in p_base:
                        if f_ext == c.F_EXT_CSV:
                            p_i_l = list(glob.glob(p_base + project.code + "/**/*" + f_ext, recursive=True))
                        elif f_ext == c.F_EXT_GEOJSON:
                            p_i_l = list(glob.glob(p_base + project.code + "/" + c.VIEW_MAP + "/*" + f_ext))
                        else:
                            p_i_l = list(glob.glob(p_base + project.code + "/*" + f_ext))
                        p_i_l = [p.replace(p_base, "") for p in p_i_l]
                        p_l = p_l + p_i_l
                        id_l = id_l + [p_base] * len(p_i_l)

                    # Google Drive path.
                    else:
                        drive_project = cl_gd.GoogleDrive(p_base.replace("gd:", ""))
                        if f_ext == c.F_EXT_CSV:
                            df_files = drive_project.glob(pattern=("**" + f_ext))
                        elif f_ext == c.F_EXT_GEOJSON:
                            df_files = drive_project.glob(pattern=(c.VIEW_MAP + "/*" + f_ext))
                        else:
                            df_files = drive_project.glob(pattern=("*" + f_ext))
                        p_i_l = list(df_files[cl_gd.PROP_PATH])
                        p_l = p_l + [project.code + "/" + p for p in p_i_l]
                        id_l = id_l + list(df_files[cl_gd.PROP_ITEM_ID])

            # Create DataFrame.
            df = pd.DataFrame()
            df[cl_gd.PROP_PATH] = p_l
            df[cl_gd.PROP_ITEM_ID] = id_l
            self.df_files = df

    def files(
        self,
        pattern: Optional[str] = ""
    ) -> pd.DataFrame:
        """
        --------------------------------------------------------------------------------------------------------------------
        Select files matching a pattern.

        Parameters
        ----------
        pattern: Optional[str] = ""
            Pattern.

        Returns
        -------
        List[str]
            Subset of 'p_l'.
        --------------------------------------------------------------------------------------------------------------------
        """

        p_l = list(self.df_files[cl_gd.PROP_PATH])

        # List the paths matching the pattern.
        if pattern != "":
            p_sel_l = []
            for p in p_l:
                match = re.match(pattern.replace("*", ".*"), p)
                if (match is not None) and (match.pos == 0) and (match.endpos == len(p)):
                    p_sel_l.append(p)
            p_l = p_sel_l

        # Select rows.
        df_sel = self.df_files.loc[self.df_files[cl_gd.PROP_PATH].isin(p_l)]

        return df_sel

    def load(
        self,
        fn_ini: str = "config.ini"
    ):

        """
        ----------------------------------------
        Load global and project parameters.

        Parameters
        ----------
        fn_ini : str
            Name of INI file.
        ----------------------------------------
        """

        # Load the parameters comprised in the global configuration file.
        self.load_global_parameters(fn_ini)

        # Load project-specific configuration file.
        project_code = self.project.code if self.project is not None else ""

        # Load the parameters comprised in the project configuration file.
        if project_code != "":
            self.load_project_parameters(project_code, fn_ini)

    def load_global_parameters(
        self,
        fn_ini: str = "config.ini"
    ):

        """
        ----------------------------------------
        Load global parameters.

        Parameters
        ----------
        fn_ini: str
            Name of INI file.
        ----------------------------------------
        """

        # Path of configuration file.
        pattern = "context/" + fn_ini
        if self.drive is not None:
            p_ini_global = list(self.files(pattern)[cl_gd.PROP_ITEM_ID])[0]
        else:
            p_ini_global = cntx.d_data + pattern

        if ((self.drive is None) and (os.path.exists(p_ini_global))) or\
           ((self.drive is not None) and (p_ini_global != "")):

            # Read file.
            config = configparser.ConfigParser()
            if self.drive is None:
                config.read(p_ini_global)
            else:
                config.read_string(str(self.drive.load_ini(p_ini_global)))

            # Loop through sections.
            for section in config.sections():

                # Loop through keys.
                for key in config[section]:

                    # Extract value.
                    value = config[section][key]

                    if (key == "projects") and (self.projects is not None):
                        project_l = str_to_arr_2d(value, float)
                        for i in range(len(self.projects.items)):
                            for j in range(len(project_l)):
                                if self.projects.items[i].code == project_l[j][0]:
                                    self.projects.items[i].desc = project_l[j][1]
                                    break

    def load_project_parameters(
        self,
        project_code: str,
        fn_ini: str = "config.ini"
    ):

        """
        ----------------------------------------
        Load global parameters.

        Parameters
        ----------
        project_code: str
            Project code.
        fn_ini : str
            Name of INI file.
        ----------------------------------------
        """

        # Directory holding the configuration file (on local ore remote drive).
        d_base = str(cl_auth.path(project_code))
        drive_proj = None

        # Load configuration file.
        pattern = project_code + "/" + fn_ini
        if "gd:" in d_base:
            d_data_proj = d_base.replace("gd:", "")
            drive_proj = cl_gd.GoogleDrive(d_data_proj)
            p_ini_project = list(self.files(pattern)[cl_gd.PROP_ITEM_ID])[0]
        else:
            p_ini_project = d_base + pattern

        if ((drive_proj is None) and (os.path.exists(p_ini_project))) or\
           ((drive_proj is not None) and (p_ini_project != "")):

            # Read file.
            config = configparser.ConfigParser()
            if drive_proj is None:
                config.read(p_ini_project)
            else:
                config.read_string(str(drive_proj.load_ini(p_ini_project)))

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
                            list(self.opt_map_centiles).sort()

                    elif key == "opt_map_locations":
                        self.opt_map_locations =\
                            pd.DataFrame(str_to_arr_2d(value, float), columns=[c.DIM_LONGITUDE, c.DIM_LATITUDE, "desc"])

                    elif key == "opt_tbl_centiles":
                        opt_tbl_centiles = str_to_arr_1d(value, int)
                        if str(opt_tbl_centiles).replace("['']", "") != "":
                            self.opt_tbl_centiles = opt_tbl_centiles
                            list(self.opt_tbl_centiles).sort()

                    elif key == "opt_ts_centiles":
                        opt_ts_centiles = str_to_arr_1d(value, int)
                        if str(opt_ts_centiles).replace("['']", "") == "":
                            self.opt_ts_centiles = opt_ts_centiles
                            list(self.opt_ts_centiles).sort()

                    elif key == "opt_cluster_centiles":
                        opt_cluster_centiles = str_to_arr_1d(value, int)
                        if str(opt_cluster_centiles).replace("['']", "") == "":
                            self.opt_cluster_centiles = opt_cluster_centiles
                            list(self.opt_cluster_centiles).sort()

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
        Get the path to data.

        Returns
        str
            Path to data.
        ----------------------------------------
        """

        return self._d_data

    def load_image(
        self,
        p: str
    ) -> Image:

        """
        ----------------------------------------
        Load an image.

        Parameters
        ----------
        p: str
            Path or directory ID.

        Returns
        -------
        Image.pyi
            Logo.
        ----------------------------------------
        """

        # Read file.
        if self.drive is None:
            image = Image.open(self.d_data + "context/" + p)
        else:
            image = self.drive.load_image(path=p)

        return image

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
