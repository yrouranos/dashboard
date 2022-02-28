# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Utilities.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
import numpy as np
import os
import pandas as pd
import simplejson
import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Union

# Dashboard libraries.
from def_constant import const as c
from def_context import cntx

warnings.filterwarnings("ignore")


def load_data(
    mode: Optional[str] = ""
) -> Union[pd.DataFrame, None]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load data.

    Parameters
    ----------
    mode : Optional[str]
        Mode.
        ts|ts_bias: mode = {"rcp", "sim"}
        cycle:      mode = {"MS", "D"}

    Returns
    -------
    pd.DataFrame
        Dataframe.

    Structure of data directory:
    +-- ouranos.png
    |
    +-- <project_code>
        |
        +-- cycle_d
        |   |
        |   +-- <vi_code>  ex: pr
        |       |
        |       +-- <hor_code>  ex: 2021-2050
        |           |
        |           +-- <vi_name>_<RCM>_<domain>_<GCM>_<rcp_code>_<hor_code.start>_<hor_code.end>_daily.csv
        |               ex: pr_HIRHAM5_AFR-44_ICHEC-EC-EARTH_rcp45_2021_2050_daily.csv
        |               columns: day,mean,min,max,var
        |                    ex: 1,7.244016214648855e-06,-3.332919823397555e-08,0.00021562011394048503,pr
        |
        +-- cycle_m
        |   |
        |   +-- <vi_code>  ex: pr
        |       |
        |       +-- <hor_code>  ex: 2021-2050
        |           |
        |           +-- <vi_name>_<RCM>_<domain>_<GCM>_<rcp_code>_<hor_code.start>_<hor_code.end>_monthly.csv
        |               ex: pr_HIRHAM5_AFR-44_ICHEC-EC-EARTH_rcp45_2021_2050_monthly.csv
        |               columns: year,1,2,3,4,5,6,7,8,9,10,11,12
        |                    ex: 2021,0.003668,0.000196,0.014072,1.344051,3.065682,28.971143,...
        +-- ts
        |   |
        |   +-- <vi_code>_<mode>.csv
        |       ex: pr_rcp.csv
        |       columns: year,ref,rcp45_moy,rcp45_min,rcp45_max,rcp85_moy,rcp85_min,rcp85_max
        |            ex: 1981,545.37,475.40,358.05,602.77,469.10,350.61,601.30
        |
        +-- ts_bias
        |   |
        |   +- <vi_code> ex: pr
        |      |
        |      +-- <vi_code>_<mode>*.csv
        |          ex: pr_rcp.csv
        |          ex: pr_sim_delta.csv
        |          columns: year,ref,rcp45_moy,rcp45_min,rcp45_max,rcp85_moy,rcp85_min,rcp85_max
        |               ex: 1981,545.37,475.40,358.05,602.77,469.10,350.61,601.30
        |
        +-- tbl
        |   |
        |   +-- <vi_code>/<vi_name>.csv
        |       ex: pr.csv
        |       columns: stn, var, rcp, hor, stat, centile, val
        |            ex: era5_land, pr, rcp45, 2021-2050, mean, -1, 486.53
        +-- map
            |
            +-- <vi_code>  ex: pr
            |   |
            |   +-- <hor_code>  ex: 2021-2050
            |       |
            |       +-- <vi_name>_<rcp_code>_<hor_code.start>_<hor_code.end>_<stat_code>.csv
            |           ex: pr_rcp45_2021_2050_mean.csv
            |           ex: pr_rcp45_2021_2050_c010.csv
            |           ex: pr_rcp45_2021_2050_c090_delta.csv
            |           columns: longitude,latitude,pr
            |                ex: -17.30,14.8,226.06
            |
            +-- boundaries.geojson
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    p = ""

    view_code  = cntx.view.code if cntx.view is not None else ""
    if view_code == c.view_cluster:
        view_code = c.view_ts
    delta_code = cntx.delta.code if cntx.delta is not None else False
    vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
    vi_name    = cntx.varidx.name if cntx.varidx is not None else ""
    vi_precision = cntx.varidx.precision if cntx.varidx is not None else 0
    hor_code   = cntx.hor.code if cntx.hor is not None else ""
    rcp_code   = cntx.rcp.code if cntx.rcp is not None else ""
    stat_code  = cntx.stat.code if cntx.stat is not None else ""
    sim_code   = cntx.sim.code if cntx.sim is not None else ""

    if view_code == c.view_tbl:
        p = cntx.d_project + "<view_code>/<vi_code>/<vi_name>.csv"
        p = p.replace("<view_code>", view_code)
        p = p.replace("<vi_code>", vi_code)
        p = p.replace("<vi_name>", vi_name)

    elif view_code in [c.view_ts, c.view_ts_bias]:
        p = cntx.d_project + "<view_code>/<vi_code>/<vi_name>_<mode>_<delta>.csv"
        p = p.replace("_<mode>", "_" + mode)
        p = p.replace("<view_code>", view_code)
        p = p.replace("<vi_code>", vi_code)
        p = p.replace("<vi_name>", vi_name)
        p = p.replace("_<delta>", "" if delta_code == "False" else "_delta")

    elif view_code == c.view_map:
        p = cntx.d_project + "<view_code>/<vi_code>/<hor_code>/*<rcp_code>*<stat>_<delta>.csv"
        p = p.replace("<view_code>", view_code)
        p = p.replace("<vi_code>", vi_code)
        p = p.replace("<hor_code>", hor_code)
        p = p.replace("<rcp_code>", rcp_code)
        p = p.replace("<stat>", stat_code)
        p = p.replace("_<delta>", "" if delta_code == "False" else "_delta")

    elif c.view_cycle in view_code:
        p = cntx.d_project + "<view_code>/<vi_code>/<hor_code>/*<sim_code>*<rcp_code>*.csv"
        view_code += "_" + mode.lower()
        p = p.replace("<view_code>", view_code)
        p = p.replace("<vi_code>", vi_code)
        p = p.replace("<hor_code>", hor_code)
        p = p.replace("<sim_code>", sim_code)
        if sim_code != "":
            p = p.replace("<rcp_code>", "")
        elif rcp_code == "":
            p = p.replace("<rcp_code>", "*")

    if (view_code == c.view_map) or (c.view_cycle in view_code):
        p_l = list(glob.glob(p))
        if len(p_l) > 0:
            p = p_l[0]

    if not os.path.exists(p):
        return None
    else:
        df = pd.read_csv(p)

    # Round values.
    if df is not None:
        n_dec = vi_precision
        if (view_code in [c.view_ts, c.view_ts_bias]) or (c.view_cycle in view_code):
            for col in df.select_dtypes("float64").columns:
                df.loc[:, col] = df.copy()[col].round(n_dec).to_numpy()
        else:
            df["val"] = df["val"].round(decimals=n_dec)

    return df


def load_geojson(
    p: str,
    out_format: str = "vertices-coords"
) -> Union[pd.DataFrame, Tuple[List[float], any]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load a geojson file.

    Parameters
    ----------
    p: str
        Path.
    out_format: str
        Format = {"vertices-coordinates", "pandas"}

    Returns
    -------
    Union[pd.DataFrame, Tuple[List[float]]]
        Vertices and coordinates, or dataframe.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Read geojson file.
    with open(p) as f:
        pydata = simplejson.load(f)

    # Extract vertices.
    coords = pydata["features"][0]["geometry"]["coordinates"][0]
    vertices = coords[0]
    if len(vertices) == 2:
        coords = pydata["features"][0]["geometry"]["coordinates"]
        vertices = coords[0]
    if out_format == "vertices":
        return vertices, coords

    # Create dataframe.
    df = pd.DataFrame()
    df["longitude"] = np.array(vertices).T.tolist()[0]
    df["latitude"] = np.array(vertices).T.tolist()[1]

    return df


def calc_range(
    centile_as_str_l: List[str]
) -> List[float]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Extract the minimum and maximum values, considering all the maps for a single variable.

    Parameters
    ----------
    centile_as_str_l: List[str]
        Lower an upper centiles as strings, e.g. ["c010", "c090"].

    Returns
    -------
    List[float]
        Minimum and maximum values.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    min_val, max_val = np.nan, np.nan

    # Codes.
    view_code  = cntx.view.code if cntx.view is not None else ""
    vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
    vi_name    = cntx.varidx.name if cntx.varidx is not None else ""
    delta_code = cntx.delta.code if cntx.delta is not None else False

    if view_code == c.view_map:
        
        # Reference file.
        p_ref = cntx.d_project + "<view>/<vi_code>/*/<vi_name>_ref*_mean.csv"
        p_ref = p_ref.replace("<view>", view_code)
        p_ref = p_ref.replace("<vi_code>", vi_code)
        p_ref = p_ref.replace("<vi_name>", vi_name)
        p_ref = glob.glob(p_ref)

        # Get centiles.
        centile_lower_as_str, centile_upper_as_str = "", ""
        if len(centile_as_str_l) >= 1:
            centile_lower_as_str = centile_as_str_l[0]
            centile_upper_as_str = centile_as_str_l[len(centile_as_str_l) - 1]

        # RCP files.
        p_rcp = cntx.d_project + "<view>/<vi_code>/*/<vi_name>_rcp*_<centile>_<delta>.csv"
        p_rcp = p_rcp.replace("<view>", view_code)
        p_rcp = p_rcp.replace("<vi_code>", vi_code)
        p_rcp = p_rcp.replace("<vi_name>", vi_name)
        p_rcp = p_rcp.replace("_<delta>", "" if delta_code == "False" else "_delta")
        p_rcp_centile_lower = glob.glob(p_rcp.replace("<centile>", centile_lower_as_str))
        p_rcp_centile_upper = glob.glob(p_rcp.replace("<centile>", centile_upper_as_str))
        p_l = p_rcp_centile_lower + p_rcp_centile_upper
        if delta_code == "False":
            p_l = p_ref + p_l

        # Find the minimum and maximum values.
        for p in p_l:
            if os.path.exists(p):
                df = pd.read_csv(p)
                min_vals = list(df["val"]) + [min_val]
                max_vals = list(df["val"]) + [max_val]
                min_val = np.nanmin(min_vals)
                max_val = np.nanmax(max_vals)

    return [min_val, max_val]


def ref_val(
) -> str:
    """
    --------------------------------------------------------------------------------------------------------------------
    Get the reference value.

    Returns
    -------
    str
        Reference value and unit.
    --------------------------------------------------------------------------------------------------------------------
    """

    df = None
    val = ""

    # Extract from table.
    if cntx.view.code == c.view_tbl:
        df = pd.DataFrame(load_data())
        val = df[df["rcp"] == c.ref]["val"][0]

    # Extract from time series.
    elif cntx.view.code in [c.view_ts, c.view_ts_bias]:
        df = pd.DataFrame(load_data("rcp"))
        val = np.nanmean(df[c.ref])

    # Adjust precision and units.
    if df is not None:
        val = round_values(val, cntx.varidx.precision)
        unit = cntx.varidx.unit
        if unit != "°C":
            val += " "
        val += unit

    return val


def get_shared_sims(
    p_l: Optional[List[str]] = None
) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the simulations that are shared between multiple variables.

    Parameters
    ----------
    p_l: Optional[List[str]]
        Path.

    Returns
    -------
    Listr[str]
        Simulations that are shared between multiple variables.
    --------------------------------------------------------------------------------------------------------------------
    """

    rcp_code = cntx.rcp.code if cntx.rcp is not None else ""

    # List simulations associated with each variable, and put them into an array.
    arr_sim_l = []
    for i in range(cntx.varidxs.count):
        cntx.varidx = cntx.varidxs.items[i]
        if cntx.varidx.is_var:
            if p_l is None:
                sim_l = pd.DataFrame(load_data("sim")).columns[2:]
            else:
                sim_l = pd.read_csv(p_l[i]).columns[2:]
            arr_sim_l.append(sim_l)

    # Identify the simulations that are available for all variables.
    sim_l = []
    for sim in arr_sim_l[0]:
        available = True
        for i in range(1, len(arr_sim_l)):
            if sim not in arr_sim_l[i]:
                available = False
                break
        if available and ((rcp_code == c.rcpxx) or ((rcp_code != c.rcpxx) and (rcp_code in sim))):
            sim_l.append(sim)

    return sim_l


def list_dir(
    p: str
) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    List sub-directories within a directory.
    
    Parameters
    ----------
    p: str
        Path.
    
    Returns
    -------
    List[str]
        List of sub-directories.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    dir_l = []
    
    for e in Path(p).iterdir():
        try:
            if Path(e).is_dir():
                dir_l.append(os.path.basename(str(e)))
        except NotADirectoryError:
            pass
    
    return dir_l


def round_values(
    val_l: Union[float, List[float]],
    n_dec: int
) -> Union[str, List[str]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Round values.

    Parameters
    ----------
    val_l: Union[float, List[float]]
        Value or list of values.
    n_dec: int
        Number of decimals.

    Returns
    -------
    Union[str, List[str]]
        Rounded values.
    --------------------------------------------------------------------------------------------------------------------
    """

    val_str_l = []

    # Transform into a list.
    if not (isinstance(val_l, List) or isinstance(val_l, pd.Series)):
        val_rounded_l = [val_l]
    else:
        val_rounded_l = val_l

    # Round each value in the list.
    for i in range(len(val_rounded_l)):
        if not np.isnan(val_rounded_l[i]):
            val_str_l.append(str("{:." + str(n_dec) + "f}").format(float(val_rounded_l[i])))
        else:
            val_str_l.append("nan")

    # Extract value if the input is not a list.
    if not (isinstance(val_l, List) or isinstance(val_l, pd.Series)):
        val_str_l = val_str_l[0]

    return val_str_l
