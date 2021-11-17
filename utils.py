import altair as alt
import glob
import numpy as np
import os
import pandas as pd
from typing import List, Optional


view_list    = ["Série temporelle", "Tableau", "Carte"]
cols         = {"rcp26": "blue", "rcp45": "green", "rcp85": "red"}
back_sidebar = "WhiteSmoke"
p_logo       = "./data/ouranos.png"

alt.renderers.enable("default")


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
        f_list = list(glob.glob("./data/" + view + "/*.csv"))
        for f in f_list:
            var_or_idx_list.append(os.path.basename(f).replace(".csv", ""))
        var_or_idx_list.sort()
    
    else:
        p = "./data/" + view + "/"
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
        p = "./data/<view>/<var_or_idx>.csv"
        p = p.replace("<view>", view)
        p = p.replace("<var_or_idx>", var_or_idx)
        df = pd.read_csv(p)
        if view == "ts":
            items = list(df.columns)
        else:
            items = df["rcp"]
    
    else:
        
        # List files.
        p = "./data/<view>/<var_or_idx>/<hor>/*.csv"
        p = p.replace("<view>", view)
        p = p.replace("<var_or_idx>", var_or_idx)
        p = p.replace("<hor>", hor)
        items = list(glob.glob(p))
    
    # Extract RCPs.
    for item in items:
        if "rcp" in item:
            rcp = item.split("_")[0 if view in ["ts", "tbl"] else 1]
            if rcp not in rcp_list:
                rcp_list.append(rcp)
    rcp_list.sort()
    
    return rcp_list


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
        p = "./data/<view>/<var_or_idx>.csv"    
    else:
        p = "./data/<view>/<var_or_idx>/<hor>/<var_or_idx>_<rcp>_<hor_>_<stat>_<delta>.csv"        
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


def gen_ts(var_or_idx: str) -> alt.Chart:

    """
    Generate a plot of time series.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
        
    Returns
    -------
    alt.Chart :
        Plot of time series.
    """
    
    # Load data.
    df = load_data(var_or_idx, "ts")

    # Extract RCPs.
    rcp_list = get_rcp_list(var_or_idx, "ts")
    
    # Extract minimum and maximum.
    y_min = df["ref"].min()
    y_max = df["ref"].max()
    for rcp in rcp_list:
        y_min = min(y_min, df[rcp + "_min"].min())
        y_max = max(y_max, df[rcp + "_max"].max())
    
    # Add layers.
    plot = None
    for rcp in rcp_list:
        
        line = alt.Chart(df.reset_index()).mark_line().encode(
            x=alt.X("year",
                    axis=alt.Axis(title="Année", format="d")),
            y=alt.Y(rcp + "_moy",
                    scale=alt.Scale(domain=[y_min, y_max]),
                    axis=alt.Axis(title=get_var_or_idx_desc(var_or_idx), format="d")),
            color=alt.value(cols[rcp]),
            tooltip=rcp + "_moy"
        ).interactive()

        band = alt.Chart(df).mark_area(opacity=0.3).encode(
            x="year",
            y=alt.Y(rcp + "_min", scale=alt.Scale(domain=[y_min, y_max])),
            y2=rcp + "_max",
            color=alt.value(cols[rcp])
        )
        
        if rcp == rcp_list[0]:
            plot = line + band
        else:
            plot = plot + line + band

    return plot.configure_axis(grid=False)


def gen_tbl(var_or_idx: str) -> pd.DataFrame:
    
    """
    Generate a table.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
        
    Returns
    -------
    pd.DataFrame :
        Dataframe.
    """
    
    # Load data.
    df = load_data(var_or_idx, "tbl")
    df = df.drop(df.columns[0:3], axis=1)
    
    return df