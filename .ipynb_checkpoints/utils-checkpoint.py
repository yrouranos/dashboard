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
import rcp_def
import glob
import math
import numpy as np
import os
import pandas as pd
import view_def
from matplotlib.lines import Line2D
from pathlib import Path
from typing import List, Optional, Tuple


def load_data(
    cntx: context_def.Context,
    stat: str="",
    q: float=-1,
    delta: bool = False
) -> pd.DataFrame:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load data.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    stat : Optional[str]
        Statistic = {"quantile", "mean"}
    q : Optional[float]
        Quantile (ex: 0.1).
    delta : Optional[bool]
        If True, return delta.
    
    Returns
    -------
    pd.DataFrame
        Dataframe.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
        p = cf.d_data + "<view>/<varidx_code>.csv"    
    else:
        if stat == "quantile":
            stat = "q" + str(math.ceil(q * 100))
        p = cf.d_data + "<view>/<varidx_code>/<hor>/<varidx_name>_<rcp>_<hor_>_<stat>_<delta>.csv"        
    p = p.replace("<view>", cntx.view.get_code())
    p = p.replace("<varidx_code>", cntx.varidx.get_code())
    p = p.replace("<varidx_name>", cntx.varidx.get_code())
    p = p.replace("<rcp>", cntx.rcp.get_code())
    p = p.replace("<hor_>", cntx.hor.get_code().replace("-", "_"))
    p = p.replace("<hor>", cntx.hor.get_code())
    p = p.replace("<stat>", stat)
    p = p.replace("_<delta>", "" if delta is False else "_delta")        
    df = pd.read_csv(p)
    
    # Round values.
    n_dec = 1 if (cntx.varidx.get_code() in [vi.var_tasmin, vi.var_tasmax]) else 0
    if cntx.view.get_code() == view_def.mode_ts:
        for col in df.columns:
            df[col] = df[col].round(decimals=n_dec)
    elif cntx.view.get_code() == view_def.mode_tbl:
        df["val"] = df["val"].round(decimals=n_dec)
    else:
        df[cntx.varidx.get_code()] = df[cntx.varidx.get_code()].round(decimals=n_dec)

    return df
    

def get_min_max(
    cntx: context_def.Context
) -> Tuple[float , float]:

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
    
    min, max = np.nan, np.nan
    
    if cntx.view.get_code() == view_def.mode_map:
        
        # Identify the files to consider.
        p_ref = glob.glob(cf.d_map + cntx.varidx.get_code() + "/*/" + cntx.varidx.get_code() + "_ref*_mean.csv")
        p_rcp = cf.d_map + cntx.varidx.get_code() + "/*/" + cntx.varidx.get_code() + "_rcp*_q<q>.csv" 
        p_rcp_q_low = glob.glob(p_rcp.replace("<q>", str(math.ceil(cf.q_l[0] * 100))))
        p_rcp_q_high = glob.glob(p_rcp.replace("<q>", str(math.ceil(cf.q_l[1] * 100))))
        p_l = p_ref + p_rcp_q_low + p_rcp_q_high

        # Find the minimum and maximum values.
        for p in p_l:
            if os.path.exists(p):
                df = pd.read_csv(p)
                min_vals = list(df[cntx.varidx.get_code()]) + [min]
                max_vals = list(df[cntx.varidx.get_code()]) + [max]
                min = np.nanmin(min_vals)
                max = np.nanmax(max_vals)

    return min, max


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
    
    list = []
    
    for e in Path(p).iterdir():
        try:
            if Path(e).is_dir():
                list.append(os.path.basename(str(e)))
        except NotADirectoryError:
            pass
    
    return list
