import config as cf
import glob
import math
import numpy as np
import os
import pandas as pd
from matplotlib.lines import Line2D
from typing import List, Optional, Tuple


def get_view_code(
    view: str
) -> str:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get the code of a view.
    
    Parameters
    ----------
    view : str
        View = {"ts", "tbl", "map"}
    
    Returns
    -------
    str
        Code.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    code = ""
    
    if view in list(cf.views.values()):
        code = list(cf.views.keys())[list(cf.views.values()).index(view)]
        
    return code


def get_varidx_list(
    view: str
) -> List[str]:
    
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get variable list.
    
    Parameters
    ----------
    view : str
        View = {"ts", "tbl", "map"}
        
    Returns
    -------
    List[str]
        Variable list.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    varidx_list = []
    
    if view in ["ts", "tbl"]:
        p = cf.d_data + "<view>/*.csv"
        p = p.replace("<view>", view)
        f_list = list(glob.glob(p))
        for f in f_list:
            varidx_list.append(os.path.basename(f).replace(".csv", ""))
        varidx_list.sort()
    
    else:
        p = cf.d_data + "<view>/"
        p = p.replace("<view>", view)
        varidx_list = os.listdir(p)
    
    return varidx_list


def get_rcp_list(
    varidx_code: str,
    view: str,
    hor: Optional[str] = ""
) -> List[str]:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get RCP list.
    
    Parameters
    ----------
    varidx_code : str
        Climate variable or index.
    view : str
        View = {"ts", "tbl", "map"}
    hor : Optional[str]
        Horizon (ex: "1981-2010")
        
    Returns
    -------
    List[str]
        RCP list.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    rcp_list = []
    
    # The list of RCPs is within data files.
    if view in ["ts", "tbl"]:
        p = cf.d_data + "<view>/<varidx_code>.csv"
        p = p.replace("<view>", view)
        p = p.replace("<varidx_code>", varidx_code)
        df = pd.read_csv(p)
        if view == "ts":
            items = list(df.columns)
        else:
            items = df["rcp"]
    
    # The list of RCPs is within file structure.
    else:
        p = cf.d_data + "<view>/<varidx_code>/<hor>/*.csv"
        p = p.replace("<view>", view)
        p = p.replace("<varidx_code>", varidx_code)
        p = p.replace("<hor>", hor)
        items = list(glob.glob(p))
    
    # Extract RCPs.
    for item in items:
        if ("rcp" in item) or (cf.rcp_ref in item):
            rcp = item.split("_")[0 if view in ["ts", "tbl"] else 1]
            if rcp not in rcp_list:
                rcp_list.append(rcp)
    rcp_list.sort()
    
    return rcp_list


def get_rcp_list_desc(rcp_list: List[str]) -> List[str]:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get a list of RCP descriptions.
    
    Parameters
    ----------
    rcp_list : List[str]
        List of RCPs.
    
    Returns
    -------
    List[str]
        List of RCP descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    rcp_list_desc = []
    
    for rcp in rcp_list:
        rcp_list_desc.append(get_rcp_desc(rcp))
    
    return rcp_list_desc


def get_rcp_desc(rcp: str) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get RCP description.
    
    Parameters
    ----------
    rcp : str
        RCP = {"rcp26", "rcp45", "rcp85"}
    
    Returns
    -------
    str
        RCP description.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    rcp_desc = ""

    if rcp == cf.rcp_ref:
        rcp_desc = "Référence"
    elif rcp == cf.rcp_26:
        rcp_desc = "RCP 2.6"
    elif rcp == cf.rcp_45:
        rcp_desc = "RCP 4.5"
    elif rcp == cf.rcp_85:
        rcp_desc = "RCP 8.5"

    return rcp_desc
    
    
def get_varidx_desc_unit(varidx_name: str) -> str:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get the description of a climate variable or index.
    
    Parameters
    ----------
    varidx_name : str
        Climate variable or index.
    
    Returns
    -------
    str
        Description.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    varidx_desc_unit = ""
    if varidx_name == "tasmin":
        varidx_desc_unit = "Température minimale (°C)"
    elif varidx_name == "tasmax":
        varidx_desc_unit = "Température maximale (°C)"
    elif varidx_name in ["pr"]:
        varidx_desc_unit = "Précipitation (mm)"
    elif varidx_name == "evspsbl":
        varidx_desc_unit = "Évapotranspiration (mm)"
    elif varidx_name == "evspsblpot":
        varidx_desc_unit = "Évapotranspiration pot. (mm)"
        
    return varidx_desc_unit


def get_varidx_desc(varidx_name: str) -> str:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get title.
    
    Parameters
    ----------
    varidx_name : str
        Climate variable or index.
    
    Returns
    -------
    str
        Title.
    --------------------------------------------------------------------------------------------------------------------
    """
        
    title = ""
    if varidx_name == "tas":
        title = "Température moyenne"
    elif varidx_name == "tasmin":
        title = "Température minimale quotidienne"
    elif varidx_name == "tasmax":
        title = "Température maximale quotidienne"
    elif varidx_name == "pr":
        title = "Précipitation"
    elif varidx_name == "evspsbl":
        title = "Évapotranspiration"
    elif varidx_name == "evspsblpot":
        title = "Évapotranspiration potentielle"
        
    return title


def get_hor_list(varidx_code: str, view: str) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get title.
    
    Parameters
    ----------
    varidx_code : str
        Climate variable or index.
    view : str
        View = {"tbl", "map"}
        
    Returns
    -------
    List[str]
        Title.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    hor_list = []
    
    # List all horizons.
    if view == "map":
        p = cf.d_map + "<varidx_code>/"
        p = p.replace("<varidx_code>", varidx_code)
        hor_list = [e for e in os.path.iterdir() if e.is_dir()]
    elif view == "tbl":
        df = load_data(varidx_code, view)
        hor_ref = df[df["rcp"] == cf.rcp_ref]["hor"][0]
        hor_list = list(dict.fromkeys(list(df["hor"])))
        hor_list.remove(hor_ref)
    hor_list.sort()
    
    # Remove the horizon that includes all years.
    min_hor, max_hor = None, None
    for hor in hor_list:
        tokens = hor.split("-")
        if min_hor is None:
            min_hor = tokens[0]
            max_hor = tokens[1]
        else:
            min_hor = min(min_hor, tokens[0])
            max_hor = max(max_hor, tokens[1])
    tot_hor = min_hor + "-" + max_hor
    if tot_hor in hor_list:
        hor_list.remove(tot_hor)

    return hor_list


def load_data(varidx_code: str, view: str, hor: str = "", rcp: str = "",
              stat: str="", q: float=-1, delta: bool = False) -> pd.DataFrame:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load data.
    
    Parameters
    ----------
    varidx_code : str
        Climate variable or index.
    view : str
        View = {"ts", "tbl", "map"}
    hor : Optional[str]
        Horizon (ex: "1981-2010")
    rcp : Optional[str]
        RCP = {"rcp26", "rcp45", "rcp85"}
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
    
    # Extract variable name.
    varidx_name = varidx_code if varidx_code in cf.variables_cordex else utils.extract_varidx_name(varidx_code)
    
    # Load data.
    if view in ["ts", "tbl"]:
        p = cf.d_data + "<view>/<varidx_code>.csv"    
    else:
        if stat == "quantile":
            stat = "q" + str(math.ceil(q * 100))
        p = cf.d_data + "<view>/<varidx_code>/<hor>/<varidx_name>_<rcp>_<hor_>_<stat>_<delta>.csv"        
    p = p.replace("<view>", view)
    p = p.replace("<varidx_code>", varidx_code)
    p = p.replace("<varidx_name>", varidx_name)
    p = p.replace("<rcp>", rcp)
    p = p.replace("<hor_>", hor.replace("-", "_"))
    p = p.replace("<hor>", hor)
    p = p.replace("<stat>", stat)
    p = p.replace("_<delta>", "" if delta is False else "_delta")        
    df = pd.read_csv(p)
    
    # Round values.
    n_dec = 1 if (varidx_name in [cf.var_cordex_tasmin, cf.var_cordex_tasmax]) else 0
    if view == "ts":
        for col in df.columns:
            df[col] = df[col].round(decimals=n_dec)
    elif view == "tbl":
        df["val"] = df["val"].round(decimals=n_dec)
    else:
        df[varidx_name] = df[varidx_name].round(decimals=n_dec)

    return df


def extract_varidx_name(
    idx_code: str
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Extract index name.

    Parameters
    ----------
    idx_code : str
        Index code.
    
    Returns
    -------
    str
        Index name.
    --------------------------------------------------------------------------------------------------------------------
    """

    pos = idx_code.rfind("_")
    if pos >= 0:
        tokens = idx_code.split("_")
        if tokens[len(tokens) - 1].isdigit():
            return idx_code[0:pos]

    return idx_code
    

def get_min_max(
    varidx_code: str,
    view: str
) -> Tuple[float , float]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series.
    
    Parameters
    ----------
    varidx_code : str
        Climate variable or index.
    view : str
        View = {"ts", "tbl", "map"}
    
    Returns
    -------
    Tuple[float, float]
        Minimum and maximum values.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    min, max = np.nan, np.nan
    
    # Extract variable name.
    varidx_name = varidx_code if varidx_code in cf.variables_cordex else utils.extract_varidx_name(varidx_code)
    
    if view == "map":
        
        # Identify the files to consider.
        p_ref = glob.glob(cf.d_map + varidx_code + "/*/" + varidx_name + "_ref*_mean.csv")
        p_rcp = cf.d_map + varidx_code + "/*/" + varidx_name + "_rcp*_q<q>.csv" 
        p_rcp_q_low = glob.glob(p_rcp.replace("<q>", str(math.ceil(cf.q_list[0] * 100))))
        p_rcp_q_high = glob.glob(p_rcp.replace("<q>", str(math.ceil(cf.q_list[1] * 100))))
        p_list = p_ref + p_rcp_q_low + p_rcp_q_high

        # Find the minimum and maximum values.
        for p in p_list:
            if os.path.exists(p):
                df = pd.read_csv(p)
                min_vals = list(df[varidx_name]) + [min]
                max_vals = list(df[varidx_name]) + [max]
                min = np.nanmin(min_vals)
                max = np.nanmax(max_vals)

    return min, max