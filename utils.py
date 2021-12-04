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

import config as cf
import context_def
import glob
import numpy as np
import os
import pandas as pd
import simplejson
import view_def
import warnings
from pandas.core.common import SettingWithCopyWarning
from pathlib import Path
from typing import List, Optional, Tuple, Union

warnings.filterwarnings("ignore")

d_data = "./data/"


def load_data(
    cntx: context_def.Context
) -> pd.DataFrame:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load data.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    
    Returns
    -------
    pd.DataFrame
        Dataframe.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl, view_def.mode_box]:
        p = get_d_data(cntx) + "<view>/<varidx_code>.csv"
    else:
        p = get_d_data(cntx) + "<view>/<varidx_code>/<hor>/<varidx_name>_<rcp>_<hor_>_<stat>_<delta>.csv"
    p = p.replace("<view>", cntx.view.get_code())
    p = p.replace("<varidx_code>", cntx.varidx.get_code())
    if cntx.view.get_code() == view_def.mode_map:
        p = p.replace("<varidx_name>", cntx.varidx.get_code())
        p = p.replace("<rcp>", cntx.rcp.get_code())
        p = p.replace("<hor_>", cntx.hor.get_code().replace("-", "_"))
        p = p.replace("<hor>", cntx.hor.get_code())
        p = p.replace("<stat>", cntx.stat.get_code())
        p = p.replace("_<delta>", "" if cntx.delta is False else "_delta")
    df = pd.read_csv(p)

    # Round values.
    n_dec = cntx.varidx.get_precision()
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_box]:
        for col in df.columns:
            if col != "year":
                df.loc[:, col] = df.copy()[col].round(n_dec).to_numpy()
    elif cntx.view.get_code() == view_def.mode_tbl:
        df["val"] = df["val"].round(decimals=n_dec)
    else:
        df[cntx.varidx.get_code()] = df[cntx.varidx.get_code()].round(decimals=n_dec)

    return df


def load_geojson(
    p: str,
    format: str = "vertices-coords"
) -> Union[pd.DataFrame, Tuple[List[float]]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load a geojson file.

    Parameters
    ----------
    p : str
        Path.
    format : str
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
    if format == "vertices":
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
    Generate a plot of time series.
    
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

    for i in range(len(vals)):
        if not np.isnan(vals[i]):
            vals[i] = str("{:." + str(n_dec) + "f}").format(float(vals[i]))

    return vals


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
    Get the base directory of data.

    Parameters
    ----------
    cntx : context_def.Context
        Context.

    Returns
    -------
    str
        Base directory of data.
    """

    d = d_data + "<project>/"
    d = d.replace("<project>/", "" if cntx.project is None else cntx.project.get_code() + "/")

    return d


def get_p_logo(
    cntx: context_def.Context
) -> str:

    """
    Get path of logo.

    Parameters
    ----------
    cntx : context_def.Context
        Context.

    Returns
    -------
    str
        Path of logo.
    """

    return "./data/ouranos.png"


def get_p_bounds(
    cntx: context_def.Context
) -> str:

    """
    Get region boundaries.

    Parameters
    ----------
    cntx : context_def.Context
        Context

    Returns
    -------
    str
        Path of geojson file containing region boundaries.
    """

    p = get_d_data(cntx) + "<view>/<project_code>_boundaries.geojson"
    p = p.replace("<view>", cntx.view.get_code())
    p = p.replace("<project_code>", cntx.project.get_code())

    return p
