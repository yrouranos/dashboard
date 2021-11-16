import altair as alt
import glob
import numpy as np
import os
import pandas as pd
import panel as pn
import panel.widgets as pnw
import streamlit as st
from typing import List

alt.renderers.enable("default")
pn.extension("vega")


def get_var_or_idx_list(view: str) -> List[str]:
    
    
    """
    Get variable list.
    
    Parameters
    ----------
    view : str
        {"ts", "tbl", "map"}
        
    Returns
    -------
    List[str]
        Variable list.
    """
    
    var_or_idx_list = []
    f_list = list(glob.glob("./data/" + view + "/*.csv"))
    for f in f_list:
        var_or_idx_list.append(os.path.basename(f).replace(".csv", ""))
    var_or_idx_list.sort()
    
    return var_or_idx_list


def get_rcp_list(var_or_idx: str, view: str) -> List[str]:
    
    """
    Get RCP list.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    view : str
        {"ts", "tbl", "map"}
        
    Returns
    -------
    List[str]
        RCP list.
    """
    
    # Load data.
    p = "./data/" + view + "/<var_or_idx>.csv"
    df = pd.read_csv(p.replace("<var_or_idx>", var_or_idx))
    
    # Extract rcp.
    rcp_list = []
    for col in df.columns:
        if "rcp" in col:
            rcp = col.replace("_min", "").replace("_max", "").replace("_moy", "")
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


def load_data(var_or_idx: str, view: str) -> pd.DataFrame:

    """
    Load data.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    view : str
        {"ts", "tbl", "map"}
    
    Returns
    -------
    pd.DataFrame
        Dataframe.
    """
    
    # Load data.
    p = "./data/" + view + "/<var_or_idx>.csv"
    df = pd.read_csv(p.replace("<var_or_idx>", var_or_idx))
    
    # Round values.
    n_dec = 1 if (var_or_idx in ["tasmin", "tasmax"]) else 0
    for col in df.columns:
        df[col] = df[col].round(decimals=n_dec)

    return df


def plot_ts(var_or_idx: str) -> alt.Chart:

    """
    Draw a plot of time series.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
        
    Returns
    -------
    alt.Chart :
        Plot.
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


def vars_update(event):
    
    """
    Variable updated.
    This is not required with streamlit.
    """
    
    if views.value == view_list[0]:
        tab_ts[0][2] = plot_ts(vars.value)

    
def views_update(event):
    
    """
    View updated.
    This is not required with streamlit.
    """
    
    if views.value == view_list[0]:
        dash[1] = tab_ts
    elif views.value == view_list[1]:
        dash[1] = tab_tbl
    else:
        dash[1] = tab_map

view_list = ["Série temporelle", "Tableau", "Carte"]
cols = {"rcp26": "blue", "rcp45": "green", "rcp85": "red"}
back_menu = "WhiteSmoke"
logo_oura = pn.Column(pn.pane.PNG("./data/ouranos.png", height=50))

tab_ts  = None
tab_tbl = None
tab_map = None

# notebook:
output_mode = "jupyter_notebook"
if output_mode == "jupyter_notebook":
    
    views = pnw.RadioBoxGroup(name="RadioBoxGroup", options=view_list, inline=False)
    views.param.watch(views_update, ["value"], onlychanged=True)
    
    vars = pnw.Select(options=get_var_or_idx_list("ts"), width=100)
    vars.param.watch(vars_update, ["value"], onlychanged=True)
    
    plot = plot_ts(vars.value)

    tab_ts  = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                               vars, plot))
    tab_tbl = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                               vars, "Under development"))
    tab_map = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                               vars, "Under development"))
    menu = pn.Column(logo_oura,
                     pn.pane.Markdown("<b>Select view</b>"),
                     views,
                     pn.Spacer(background=back_menu, sizing_mode="stretch_both"),
                     background=back_menu,
                     width=200)
    dash = pn.Row(menu, tab_ts)

# streamlit:
else:
    views = st.sidebar.radio("Select view", view_list)
    if views == view_list[0]:
        vars = st.selectbox("Variable", options=get_var_or_idx_list("ts"))
        st.write(plot_ts(vars))
    elif views == view_list[1]:
        vars = st.selectbox("Variable", options=get_var_or_idx_list("tbl"))
    else:
        vars = st.selectbox("Variable", options=get_var_or_idx_list("map"))