import glob
import numpy as np
import os
import pandas as pd
from matplotlib.lines import Line2D
from typing import List, Optional

ref          = "ref"
rcp26        = "rcp26"
rcp45        = "rcp45"
rcp85        = "rcp85"
back_sidebar = "WhiteSmoke"
d_data       = "./data/"
d_ts         = d_data + "ts/"
d_tbl        = d_data + "tbl/"
d_map        = d_data + "map/"
p_logo       = d_data + "ouranos_transparent.png"


def get_var_or_idx_list(view: str) -> List[str]:
    
    
    """
    Get variable list.
    
    Parameters
    ----------
    view : str
        View = {"ts", "tbl", "map"}
        
    Returns
    -------
    List[str]
        Variable list.
    """
    
    var_or_idx_list = []
    
    if view in ["ts", "tbl"]:
        p = d_data + "<view>/*.csv"
        p = p.replace("<view>", view)
        f_list = list(glob.glob(p))
        for f in f_list:
            var_or_idx_list.append(os.path.basename(f).replace(".csv", ""))
        var_or_idx_list.sort()
    
    else:
        p = d_data + "<view>/"
        p = p.replace("<view>", view)
        var_or_idx_list = os.listdir(p)
    
    return var_or_idx_list


def get_rcp_list(var_or_idx: str, view: str, hor: Optional[str] = "") -> List[str]:
    
    """
    Get RCP list.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    view : str
        View = {"ts", "tbl", "map"}
    hor : Optional[str]
        Horizon (ex: "1981-2010")
        
    Returns
    -------
    List[str]
        RCP list.
    """
    
    rcp_list = []
        
    if view in ["ts", "tbl"]:
        
        # Load data. 
        p = d_data + "<view>/<var_or_idx>.csv"
        p = p.replace("<view>", view)
        p = p.replace("<var_or_idx>", var_or_idx)
        df = pd.read_csv(p)
        if view == "ts":
            items = list(df.columns)
        else:
            items = df["rcp"]
    
    else:
        
        # List files.
        p = d_data + "<view>/<var_or_idx>/<hor>/*.csv"
        p = p.replace("<view>", view)
        p = p.replace("<var_or_idx>", var_or_idx)
        p = p.replace("<hor>", hor)
        items = list(glob.glob(p))
    
    # Extract RCPs.
    for item in items:
        if ("rcp" in item) or (ref in item):
            rcp = item.split("_")[0 if view in ["ts", "tbl"] else 1]
            if rcp not in rcp_list:
                rcp_list.append(rcp)
    rcp_list.sort()
    
    return rcp_list


def get_rcp_list_desc(rcp_list: List[str]) -> List[str]:
    
    """
    Get a list of RCP descriptions.
    
    Parameters
    ----------
    rcp_list : List[str]
        List of RCPs.
    
    Returns
    -------
    List[str]
        List of RCP descriptions.
    """
    
    rcp_list_desc = []
    
    for rcp in rcp_list:
        rcp_list_desc.append(get_rcp_desc(rcp))
    
    return rcp_list_desc


def get_rcp_desc(rcp: str) -> str:

    """
    Get RCP description.
    
    Parameters
    ----------
    rcp : str
        RCP = {"rcp26", "rcp45", "rcp85"}
    
    Returns
    -------
    str
        RCP description.
    """
    
    rcp_desc = ""

    if rcp == ref:
        rcp_desc = "Référence"
    elif rcp == rcp26:
        rcp_desc = "RCP 2.6"
    elif rcp == rcp45:
        rcp_desc = "RCP 4.5"
    elif rcp == rcp85:
        rcp_desc = "RCP 8.5"

    return rcp_desc
    
    
def get_var_or_idx_desc(var_or_idx: str) -> str:
    
    """
    Get the description of a climate variable or index.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    
    Returns
    -------
    str
        Description.
    """
    
    var_desc = ""
    if var_or_idx == "tasmin":
        var_desc = "Température minimale (°C)"
    elif var_or_idx == "tasmax":
        var_desc = "Température maximale (°C)"
    elif var_or_idx in ["pr"]:
        var_desc = "Précipitation (mm)"
    elif var_or_idx == "evspsbl":
        var_desc = "Évapotranspiration (mm)"
    elif var_or_idx == "evspsblpot":
        var_desc = "Évapotranspiration pot. (mm)"
        
    return var_desc


def get_var_or_idx_name(var_or_idx: str) -> str:
    
    """
    Get title.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    
    Returns
    -------
    str
        Title.
    """
        
    title = ""
    if var_or_idx == "tas":
        title = "Température moyenne"
    elif var_or_idx == "tasmin":
        title = "Température minimale quotidienne"
    elif var_or_idx == "tasmax":
        title = "Température maximale quotidienne"
    elif var_or_idx == "pr":
        title = "Précipitation"
    elif var_or_idx == "evspsbl":
        title = "Évapotranspiration"
    elif var_or_idx == "evspsblpot":
        title = "Évapotranspiration potentielle"
        
    return title


def get_hor_list(var_or_idx: str) -> List[str]:

    """
    Get title.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    
    Returns
    -------
    List[str]
        Title.
    """
    
    # List all horizons.
    p = d_map + "<var_or_idx>/"
    p = p.replace("<var_or_idx>", var_or_idx)
    hor_list = os.listdir(p)
    
    # Remove hte horizon that includes all years.
    min_hor, max_hor = None, None
    for hor in hor_list:
        tokens = hor.split("-")
        if min_hor is None:
            min_hor = tokens[0]
            max_hor = tokens[1]
        else:
            min_hor = min(min_hor, tokens[0])
            max_hor = max(max_hor, tokens[1])
    hor_list.remove(min_hor + "-" + max_hor)

    return hor_list
    

def load_data(var_or_idx: str, view: str, rcp: str = "", hor: str = "",
              stat: str="", delta: bool = False) -> pd.DataFrame:

    """
    Load data.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    view : str
        View = {"ts", "tbl", "map"}
    rcp : Optional[str]
        RCP = {"rcp26", "rcp45", "rcp85"}
    hor : Optional[str]
        Horizon (ex: "1981-2010")
    stat : Optional[str]
        Statistic = {"q10", "mean", "q90"}
    delta : Optional[bool]
        If True, return delta.
    
    Returns
    -------
    pd.DataFrame
        Dataframe.
    """
    
    # Load data.
    if view in ["ts", "tbl"]:
        p = d_data + "<view>/<var_or_idx>.csv"    
    else:
        p = d_data + "<view>/<var_or_idx>/<hor>/<var_or_idx>_<rcp>_<hor_>_<stat>_<delta>.csv"        
    p = p.replace("<view>", view)
    p = p.replace("<var_or_idx>", var_or_idx)
    p = p.replace("<rcp>", rcp)
    p = p.replace("<hor_>", hor.replace("-", "_"))
    p = p.replace("<hor>", hor)
    p = p.replace("<stat>", stat)
    p = p.replace("_<delta>", "" if delta is False else "_delta")        
    df = pd.read_csv(p)
    
    # Round values.
    n_dec = 1 if (var_or_idx in ["tasmin", "tasmax"]) else 0
    if view == "ts":
        for col in df.columns:
            df[col] = df[col].round(decimals=n_dec)
    elif view == "tbl":
        df["val"] = df["val"].round(decimals=n_dec)
    else:
        df[var_or_idx] = df[var_or_idx].round(decimals=n_dec)

    return df
