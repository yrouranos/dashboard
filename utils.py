# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Utilities.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import context_def
import glob
import numpy as np
import os
import pandas as pd
import rcp_def
import simplejson
import view_def
import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Union

warnings.filterwarnings("ignore")

d_data = "./data/"


def load_data(
    cntx: context_def.Context,
    cat: Optional[str] = ""
) -> Union[pd.DataFrame, None]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load data.

    Structure of data directory:
    +-- ouranos.png
    |
    +-- <project_code>
        |
        +-- disp-d
        |   |
        |   +-- <varidx_code>  ex: pr
        |       |
        |       +-- <hor_code>  ex: 2021-2050
        |           |
        |           +-- <varidx_name>_<RCM>_<domain>_<GCM>_<rcp_code>_<hor_code.start>_<hor_code.end>_daily.csv
        |                 ex: pr_HIRHAM5_AFR-44_ICHEC-EC-EARTH_rcp45_2021_2050_daily.csv
        |               columns: day,mean,min,max,var
        |                    ex: 1,7.244016214648855e-06,-3.332919823397555e-08,0.00021562011394048503,pr
        |
        +-- disp-m
        |   |
        |   +-- <varidx_code>  ex: pr
        |       |
        |       +-- <hor_code>  ex: 2021-2050
        |           |
        |           +-- <varidx_name>_<RCM>_<domain>_<GCM>_<rcp_code>_<hor_code.start>_<hor_code.end>_monthly.csv
        |                 ex: pr_HIRHAM5_AFR-44_ICHEC-EC-EARTH_rcp45_2021_2050_monthly.csv
        |               columns: year,1,2,3,4,5,6,7,8,9,10,11,12
        |                    ex: 2021,0.003668,0.000196,0.014072,1.344051,3.065682,28.971143,...
        +-- ts
        |   |
        |   +-- <varidx_code>.csv
        |         ex: pr.csv
        |       columns: year,ref,rcp45_moy,rcp45_min,rcp45_max,rcp85_moy,rcp85_min,rcp85_max
        |            ex: 1981,545.37,475.40,358.05,602.77,469.10,350.61,601.30
        |
        +-- tbl
        |   |
        |   +-- <varidx_code>.csv
        |         ex: pr.csv
        |       columns: stn, var, rcp, hor, stat, q, val
        |            ex: era5_land, pr, rcp45, 2021-2050, mean, -1, 486.53
        +-- map
            |
            +-- <varidx_code>  ex: pr
            |   |
            |   +-- <hor_code>  ex: 2021-2050
            |       |
            |       +-- <varidx_name>_<rcp_code>_<hor_code.start>_<hor_code.end>_<stat_code>.csv
            |             ex: pr_rcp45_2021_2050_mean.csv
            |             ex: pr_rcp45_2021_2050_q10.csv
            |             ex: pr_rcp45_2021_2050_q90_delta.csv
            |           columns: longitude,latitude,pr
            |                ex: -17.30,14.8,226.06
            |
            +-- boundaries.geojson
            +-- locations.csv

    Parameters
    ----------
    cntx : context_def.Context
        Context.
    cat : Optional[str]
        Data category. This is required if several types of elements are comprised in a view.
    
    Returns
    -------
    pd.DataFrame
        Dataframe.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    p = ""
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
        p = get_d_data(cntx) + "<view>/<varidx_code>.csv"
    elif cntx.view.get_code() == view_def.mode_map:
        p = get_d_data(cntx) + "<view>/<varidx_code>/<hor_code>/*_<rcp_code>_*_<stat>_<delta>.csv"
    elif cntx.view.get_code() == view_def.mode_disp:
        p = get_d_data(cntx) + "<view>/<varidx_code>/<hor_code>/*<model_code>*<rcp_code>*.csv"
    p = p.replace("<view>", cntx.view.get_code() + ("-" + cat.lower() if cat != "" else ""))
    p = p.replace("<varidx_code>", cntx.varidx.get_code())
    if cntx.view.get_code() in [view_def.mode_map, view_def.mode_disp]:
        p = p.replace("<hor_code>", cntx.hor.get_code())
        p = p.replace("<rcp_code>", cntx.rcp.get_code())
        if cntx.view.get_code() == view_def.mode_map:
            p = p.replace("<stat>", cntx.stat.get_code())
            p = p.replace("_<delta>", "" if cntx.delta is False else "_delta")
        elif cntx.view.get_code() == view_def.mode_disp:
            model_code = cntx.model.get_code() if cntx.rcp.get_code() != rcp_def.rcp_ref else ""
            p = p.replace("<model_code>", model_code)
        p = list(glob.glob(p))[0]

    if not os.path.exists(p):
        return None
    else:
        df = pd.read_csv(p)

    # Round values.
    n_dec = cntx.varidx.get_precision()
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_disp]:
        for col in df.select_dtypes("float64").columns:
            df.loc[:, col] = df.copy()[col].round(n_dec).to_numpy()
    elif cntx.view.get_code() == view_def.mode_tbl:
        df["val"] = df["val"].round(decimals=n_dec)
    else:
        df[cntx.varidx.get_code()] = df[cntx.varidx.get_code()].round(decimals=n_dec)

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
    p : str
        Path.
    out_format : str
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
    coordinates = pydata["features"][0]["geometry"]["coordinates"][0]
    vertices = coordinates[0]
    if len(vertices) == 2:
        coordinates = pydata["features"][0]["geometry"]["coordinates"]
        vertices = coordinates[0]
    if out_format == "vertices":
        return vertices, coordinates

    # Create dataframe.
    df = pd.DataFrame()
    df["longitude"] = np.array(vertices).T.tolist()[0]
    df["latitude"] = np.array(vertices).T.tolist()[1]

    return df


def get_min_max(
    cntx: context_def.Context
) -> Tuple[float, float]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Extract the minimum and maximum values, considering all the maps for a single variable.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    
    Returns
    -------
    Tuple[float, float]
        Minimum and maximum values.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    min_val, max_val = np.nan, np.nan
    
    if cntx.view.get_code() == view_def.mode_map:
        
        # Reference file.
        p_ref = get_d_data(cntx) + "<view>/<varidx_code>/*/<varidx_code>_ref*_mean.csv"
        p_ref = p_ref.replace("<view>", cntx.view.get_code())
        p_ref = p_ref.replace("<varidx_code>", cntx.varidx.get_code())
        p_ref = glob.glob(p_ref)

        # RCP files.
        p_rcp = get_d_data(cntx) + "<view>/<varidx_code>/*/<varidx_code>_rcp*_q<q>_<delta>.csv"
        p_rcp = p_rcp.replace("<view>", cntx.view.get_code())
        p_rcp = p_rcp.replace("<varidx_code>", cntx.varidx.get_code())
        p_rcp = p_rcp.replace("_<delta>", "" if cntx.delta is False else "_delta")
        p_rcp_q_low = glob.glob(p_rcp.replace("<q>", cntx.project.get_quantiles_as_str()[0]))
        p_rcp_q_high = glob.glob(p_rcp.replace("<q>", cntx.project.get_quantiles_as_str()[1]))
        p_l = p_rcp_q_low + p_rcp_q_high
        if not cntx.delta:
            p_l = p_ref + p_l

        # Find the minimum and maximum values.
        for p in p_l:
            if os.path.exists(p):
                df = pd.read_csv(p)
                min_vals = list(df[cntx.varidx.get_code()]) + [min_val]
                max_vals = list(df[cntx.varidx.get_code()]) + [max_val]
                min_val = np.nanmin(min_vals)
                max_val = np.nanmax(max_vals)

    return min_val, max_val


def list_dir(
    p: str
) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    List sub-directories within a directory.
    
    Parameters
    ----------
    p : str
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


def get_d_data(
    cntx: context_def.Context
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the base directory of data.

    Parameters
    ----------
    cntx : context_def.Context
        Context.

    Returns
    -------
    str
        Base directory of data.
    --------------------------------------------------------------------------------------------------------------------
    """

    d = d_data + "<project_code>/"
    d = d.replace("<project_code>/", "" if cntx.project is None else cntx.project.get_code() + "/")

    return d


def get_p_logo() -> str:

    """
    Get path of logo.

    Returns
    -------
    str
        Path of logo.
    """

    return "./data/ouranos.png"


def get_p_locations(
    cntx: context_def.Context
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the path of the file defining locations.

    Parameters
    ----------
    cntx : context_def.Context
        Context

    Returns
    -------
    str
        Path of CSV file containing region boundaries.
    --------------------------------------------------------------------------------------------------------------------
    """

    p = get_d_data(cntx) + "map/locations.csv"

    return p


def get_p_bounds(
    cntx: context_def.Context
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the path of the file defining region boundaries.

    Parameters
    ----------
    cntx : context_def.Context
        Context

    Returns
    -------
    str
        Path of geojson file containing region boundaries.
    --------------------------------------------------------------------------------------------------------------------
    """

    p = get_d_data(cntx) + "<view_code>/boundaries.geojson"
    p = p.replace("<view_code>", cntx.view.get_code())

    return p


def round_values(vals: List[float], n_dec: int) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Round values.

    Parameters
    ----------
    vals : List[float]
        Values.
    n_dec : int
        Number of decimals.

    Returns
    -------
    List[str]
        Rounded values.
    --------------------------------------------------------------------------------------------------------------------
    """

    vals_str = []

    for i in range(len(vals)):
        if not np.isnan(vals[i]):
            vals_str.append(str("{:." + str(n_dec) + "f}").format(float(vals[i])))
        else:
            vals_str.append("nan")

    return vals_str
