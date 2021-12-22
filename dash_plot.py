# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Plotting functions.
# - time series;
# - table of statistics;
# - map.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import altair as alt
import dash_utils
import def_context
import def_lib
import def_rcp
import def_stat
import def_varidx as vi
import def_view
import holoviews as hv
import hvplot.pandas
import math
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import panel as pn
import plotly.graph_objects as go
import plotly.io as pio
import xarray as xr
from bokeh.models import FixedTicker
from descartes import PolygonPatch
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import Union, List, Optional

alt.renderers.enable("default")
pn.extension("vega")
hv.extension("bokeh", logo=False)
pio.renderers.default = "iframe"

mode_rcp = "rcp"
mode_sim = "sim"


def gen_ts(
    cntx: def_context.Context,
    df: pd.DataFrame,
    mode: Optional[str] = mode_rcp
) -> Union[alt.Chart, any, plt.figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series.
    
    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    mode : Optional[str]
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    Union[alt.Chart, any, plt.figure] :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Extract minimum and maximum x-values (round to lower and upper decades).
    x_min = math.floor(min(df["year"]) / 10) * 10
    x_max = math.ceil(max(df["year"]) / 10) * 10

    # Extract minimum and maximum y-values.
    first_col_index = 2 if mode == mode_sim else 1
    y_min = df.iloc[:, first_col_index:].min().min()
    y_max = df.iloc[:, first_col_index:].max().max()

    # Plot components.
    x_label = "Année"
    y_label = ("Δ" if cntx.delta else "") + cntx.varidx.get_label()
    
    if cntx.lib.get_code() == def_lib.mode_mat:
        ts = gen_ts_mat(cntx, df, x_label, y_label, [x_min, x_max], [y_min, y_max], mode)
    elif cntx.lib.get_code() == def_lib.mode_hv:
        ts = gen_ts_hv(cntx, df, x_label, y_label, [y_min, y_max], mode)
    else:
        ts = gen_ts_alt(cntx, df, x_label, y_label, [y_min, y_max], mode)
        
    return ts


def gen_ts_alt(
    cntx: def_context.Context,
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
    y_range: List[float],
    mode: str
) -> alt.Chart:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series using altair.
    
    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    x_label : str
        X-label.
    y_label : str
        Y-label.
    y_range : List[str]
        Range of y_values to display [{y_min}, {y_max}].
        Dataframe.
    mode : str
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    alt.Chart :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Move reference RCP at the end of the list.
    rcps = cntx.rcps.copy()
    rcps.remove_items(def_rcp.rcp_ref, inplace=True)
    rcps.add_items(def_rcp.RCP(def_rcp.rcp_ref), inplace=True)

    # Plot components.
    x_axis = alt.Axis(title=x_label, format="d")
    y_axis = alt.Axis(title=y_label, format="d")
    y_scale = alt.Scale(domain=y_range)
    col_legend = alt.Legend(title="", orient="top-left", direction="horizontal", symbolType="stroke")
    col_scale = alt.Scale(range=cntx.rcps.get_color_l(), domain=cntx.rcps.get_desc_l())
    
    # Add layers.
    plot = None
    for item in ["area", "curve"]:

        for rcp in rcps.items:

            if (item == "area") and (rcp.get_code() == def_rcp.rcp_ref):
                continue

            # Subset columns.
            df_rcp = pd.DataFrame()
            df_rcp["Année"] = df["year"]
            df_rcp["Scénario"] = [rcp.get_desc()] * len(df)
            if rcp.get_code() == def_rcp.rcp_ref:
                df_rcp["Min"] = df_rcp["Moy"] = df_rcp["Max"] = df[def_rcp.rcp_ref]
            else:
                if mode == mode_rcp:
                    df_rcp["Min"] = df[str(rcp.get_code() + "_min")]
                    df_rcp["Moy"] = df[str(rcp.get_code() + "_moy")]
                    df_rcp["Max"] = df[str(rcp.get_code() + "_max")]
                else:
                    for column in df.columns:
                        if rcp.get_code() in column:
                            df_rcp[column] = df[column]
                    n_col = len(df_rcp.columns)
                    df_rcp["Min"] = df[2:(n_col - 1)].min(axis=1)
                    df_rcp["Moy"] = df[2:(n_col - 1)].mean(axis=1)
                    df_rcp["Max"] = df[2:(n_col - 1)].max(axis=1)

            # Round values.
            n_dec = cntx.varidx.get_precision()
            df_rcp["Moyenne"] = dash_utils.round_values(df_rcp["Moy"], n_dec)
            if rcp.get_code() == def_rcp.rcp_ref:
                tooltip = ["Année", "Scénario", "Moyenne"]
            else:
                df_rcp["Minimum"] = dash_utils.round_values(df_rcp["Min"], n_dec)
                df_rcp["Maximum"] = dash_utils.round_values(df_rcp["Max"], n_dec)
                tooltip = ["Année", "Scénario", "Minimum", "Moyenne", "Maximum"]

            # Draw area.
            if (item == "area") and (mode == mode_rcp):
                area = alt.Chart(df_rcp).mark_area(opacity=0.3, text=rcp.get_desc()).encode(
                    x=alt.X("Année", axis=x_axis),
                    y=alt.Y("Min", axis=y_axis, scale=y_scale),
                    y2="Max",
                    color=alt.Color("Scénario", scale=col_scale)
                )
                plot = area if plot is None else plot + area
            
            # Draw curve(s).
            elif item == "curve":
                if ((mode == mode_rcp) and (not cntx.delta)) or \
                   ((not cntx.delta) and (rcp.get_code() == def_rcp.rcp_ref)) or \
                   ((mode == mode_rcp) and cntx.delta and (rcp.get_code() != def_rcp.rcp_ref)):
                    opacity = 1.0
                else:
                    opacity = 0.3
                columns = ["Moy"] if (mode == mode_rcp) or (rcp.get_code() == def_rcp.rcp_ref) else []
                if mode == mode_sim:
                    for column in df_rcp.columns:
                        if rcp.get_code() in column:
                            columns.append(column)
                for column in columns:
                    if cntx.delta and (rcp.get_code() == def_rcp.rcp_ref):
                        curve = alt.Chart(df_rcp).mark_line(opacity=opacity).encode(
                            x=alt.X("Année", axis=x_axis),
                            y=alt.Y(column, axis=y_axis, scale=y_scale)
                        )
                    else:
                        curve = alt.Chart(df_rcp).mark_line(opacity=opacity, text=rcp.get_desc()).encode(
                            x=alt.X("Année", axis=x_axis),
                            y=alt.Y(column, axis=y_axis, scale=y_scale),
                            color=alt.Color("Scénario", scale=col_scale, legend=col_legend),
                            tooltip=tooltip
                        ).interactive()
                    plot = curve if plot is None else plot + curve

    # Adjust size.
    height = 362 if cntx.code == def_context.code_streamlit else 300
    plot = plot.configure_axis(grid=False).properties(height=height, width=650)

    return plot


def gen_ts_hv(
    cntx: def_context.Context,
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
    y_range: List[float],
    mode: str
) -> any:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series using hvplot.
    
    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    x_label : str
        X-label.
    y_label : str
        Y-label.
    y_range : List[str]
        Range of y_values to display [{y_min}, {y_max}].
        Dataframe.
    mode : str
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    any :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Move reference RCP at the end of the list.
    rcps = cntx.rcps.copy()
    rcps.remove_items(def_rcp.rcp_ref, inplace=True)
    rcps.add_items(def_rcp.RCP(def_rcp.rcp_ref), inplace=True)

    # Loop through RCPs.
    plot = None
    for item in ["area", "curve"]:

        for rcp in rcps.items:

            if (item == "area") and (rcp.get_code() == def_rcp.rcp_ref):
                continue

            # Subset and rename columns.
            df_rcp = pd.DataFrame()
            df_rcp["Année"] = df["year"]
            df_rcp["Scénario"] = [rcp.get_desc()] * len(df_rcp)
            if rcp.get_code() == def_rcp.rcp_ref:
                df_rcp["Minimum"] = df_rcp["Moyenne"] = df_rcp["Maximum"] = df[def_rcp.rcp_ref]
            else:
                if mode == mode_rcp:
                    if str(rcp.get_code() + "_min") in df.columns:
                        df_rcp["Minimum"] = df[str(rcp.get_code() + "_min")]
                    if str(rcp.get_code() + "_moy") in df.columns:
                        df_rcp["Moyenne"] = df[str(rcp.get_code() + "_moy")]
                    if str(rcp.get_code() + "_max") in df.columns:
                        df_rcp["Maximum"] = df[str(rcp.get_code() + "_max")]
                else:
                    for column in df.columns:
                        if rcp.get_code() in column:
                            df_rcp[column] = df[column]
                    n_col = len(df_rcp.columns)
                    df_rcp["Minimum"] = df[2:(n_col - 1)].min(axis=1)
                    df_rcp["Moyenne"] = df[2:(n_col - 1)].mean(axis=1)
                    df_rcp["Maximum"] = df[2:(n_col - 1)].max(axis=1)

            # Round values.
            n_dec = cntx.varidx.get_precision()
            df_rcp["Moyenne"] = np.array(dash_utils.round_values(df_rcp["Moyenne"], n_dec)).astype(float)
            if rcp.get_code() == def_rcp.rcp_ref:
                tooltip = ["Année", "Scénario", "Moyenne"]
            else:
                df_rcp["Minimum"] = np.array(dash_utils.round_values(df_rcp["Minimum"], n_dec)).astype(float)
                df_rcp["Maximum"] = np.array(dash_utils.round_values(df_rcp["Maximum"], n_dec)).astype(float)
                tooltip = ["Année", "Scénario", "Minimum", "Moyenne", "Maximum"]

            # Draw area.
            if (item == "area") and (mode == mode_rcp):
                area_alpha = 0.3
                area = df_rcp.hvplot.area(x="Année", y="Minimum", y2="Maximum", ylim=y_range,
                                          color=rcp.get_color(), alpha=area_alpha, line_alpha=0)
                plot = area if plot is None else plot * area

            # Draw curve(s).
            elif item == "curve":
                if ((mode == mode_rcp) and (not cntx.delta)) or \
                   ((not cntx.delta) and (rcp.get_code() == def_rcp.rcp_ref)) or \
                   ((mode == mode_rcp) and cntx.delta and (rcp.get_code() != def_rcp.rcp_ref)):
                    line_alpha = 1.0
                else:
                    line_alpha = 0.3
                show_ref = (mode == mode_rcp) or ((mode == mode_sim) and (rcp.get_code() == def_rcp.rcp_ref))
                columns = ["Moyenne"] if show_ref else []
                if mode == mode_sim:
                    for column in df_rcp.columns:
                        if rcp.get_code() in column:
                            columns.append(column)
                for column in columns:
                    curve = df_rcp.hvplot.line(x="Année", y=column, ylim=y_range,
                                               color=rcp.get_color(), line_alpha=line_alpha, label=rcp.get_desc(),
                                               hover_cols=tooltip)
                    plot = curve if plot is None else plot * curve
            
    # Adjust size and add legend.
    plot = plot.opts(legend_position="top_left", legend_opts={"click_policy": "hide", "orientation": "horizontal"},
                     frame_height=300, frame_width=645, border_line_alpha=0.0, background_fill_alpha=0.0,
                     xlabel=x_label, ylabel=y_label)

    return plot


def gen_ts_mat(
    cntx: def_context.Context,
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
    x_range: List[float],
    y_range: List[float],
    mode: str
) -> plt.Figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series using matplotlib.
    
    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    x_label : str
        X-label.
    y_label : str
        Y-label.
    x_range : List[float]
        Range of x_values to display [{x_min}, {x_max}].
    y_range : List[float]
        Range of y_values to display [{y_min}, {y_max}].
    mode : str
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    plt.Figure :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs            = 9 if cntx.code == def_context.code_streamlit else 10
    fs_labels     = fs
    fs_ticks      = fs

    # Initialize figure and axes.
    if def_context.code_streamlit in cntx.code:
        fig = plt.figure(figsize=(9, 4.4), dpi=cntx.dpi)
    else:
        fig = plt.figure(figsize=(10.6, 4.8), dpi=cntx.dpi)
        plt.subplots_adjust(top=0.98, bottom=0.10, left=0.08, right=0.92, hspace=0.0, wspace=0.0)
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:])

    # Format.
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.tick_params(axis="x", labelsize=fs_ticks, length=5)
    ax.tick_params(axis="y", labelsize=fs_ticks, length=5)
    ax.set_xticks(range(x_range[0], x_range[1] + 10, 10), minor=False)
    ax.set_xticks(range(x_range[0], x_range[1] + 5, 5), minor=True)
    plt.xlim(x_range[0], x_range[1])
    plt.ylim(y_range[0], y_range[1])

    # Move reference RCP at the end of the list.
    rcps = cntx.rcps.copy()
    rcps.remove_items(def_rcp.rcp_ref, inplace=True)
    rcps.add_items(def_rcp.RCP(def_rcp.rcp_ref), inplace=True)

    # Loop through RCPs.
    leg_labels = []
    leg_lines = []
    for rcp in rcps.items:

        # Extract columns.
        df_year = df.year
        columns = []
        if mode == mode_rcp:
            if rcp.get_code() in df.columns:
                columns = [rcp.get_code()]
            elif str(rcp.get_code() + "_moy") in df.columns:
                columns = [rcp.get_code() + "_min", rcp.get_code() + "_moy", rcp.get_code() + "_max"]
        else:
            for column in df.columns:
                if rcp.get_code() in column:
                    columns.append(column)
        df_rcp = df[columns]

        # Skip if no data is available for this RCP.
        if len(df_rcp) == 0:
            continue

        # Add curves and areas.
        color = rcp.get_color()
        area_alpha = 0.3
        if ((mode == mode_rcp) and (not cntx.delta)) or \
                ((not cntx.delta) and (rcp.get_code() == def_rcp.rcp_ref)) or \
                ((mode == mode_rcp) and cntx.delta and (rcp.get_code() != def_rcp.rcp_ref)):
            line_alpha = 1.0
        else:
            line_alpha = 0.3
        if rcp.get_code() == def_rcp.rcp_ref:
            ax.plot(df_year, df_rcp, color=color, alpha=line_alpha)
        else:
            if mode == mode_rcp:
                ax.plot(df_year, df_rcp[columns[1]], color=color, alpha=line_alpha)
                ax.fill_between(np.array(df_year), df_rcp[columns[0]], df_rcp[columns[2]], color=color,
                                alpha=area_alpha)
            else:
                for i in range(len(columns)):
                    ax.plot(df_year, df_rcp[columns[i]], color=color, alpha=line_alpha)
        
        # Collect legend label and line.
        leg_labels.append(rcp.get_desc())    
        leg_lines.append(Line2D([0], [0], color=color, lw=2))

    # Legend.
    ax.legend(leg_lines, leg_labels, loc="upper left", ncol=len(leg_labels), mode="expland", frameon=False,
              fontsize=fs_labels)

    plt.close(fig)
    
    return fig


def gen_tbl(
    cntx: def_context.Context
) -> Union[pd.DataFrame, go.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a table.
    
    Parameters
    ----------
    cntx : def_context.Context
        Context.

    Returns
    -------
    Union[pd.DataFrame, go.Figure] :
        Dataframe or figure.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    df = dash_utils.load_data(cntx)

    # List of statistics (in a column).
    stat_l, stat_desc_l = [], []
    for code in list(def_stat.get_code_desc().keys()):
        if code in [def_stat.mode_min, def_stat.mode_max, def_stat.mode_mean]:
            stat_l.append([code, -1])
        elif code == "q" + cntx.project.get_quantiles_as_str()[0]:
            stat_l.append(["quantile", cntx.project.get_quantiles()[0]])
        elif code == "q" + cntx.project.get_quantiles_as_str()[1]:
            stat_l.append(["quantile", cntx.project.get_quantiles()[1]])
        else:
            stat_l.append(["quantile", 0.5])
        stat_desc_l.append(def_stat.get_code_desc()[code])

    # Initialize resulting dataframe.
    df_res = pd.DataFrame()
    df_res["Statistique"] = stat_desc_l

    # Loop through RCPs.
    columns = []
    for rcp in cntx.rcps.items:

        if rcp.get_code() == def_rcp.rcp_ref:
            continue

        # Extract delta.
        delta = 0.0
        if cntx.delta:
            delta = float(df[df["rcp"] == def_rcp.rcp_ref]["val"])

        # Extract statistics.
        vals = []
        for stat in stat_l:
            df_cell = float(df[(df["rcp"] == rcp.get_code()) &
                               (df["hor"] == cntx.hor.get_code()) &
                               (df["stat"] == stat[0]) &
                               (df["q"] == stat[1])]["val"])
            val = df_cell - delta
            vals.append(val)

        df_res[rcp.get_code()] = vals
        if cntx.varidx.get_precision() == 0:
            df_res[rcp.get_code()] = df_res[rcp.get_code()].astype(int)

        columns.append(rcp.get_desc())

    df_res.columns = [df_res.columns[0]] + columns

    if cntx.code == def_context.code_jupyter:
        res = df_res.set_index(df_res.columns[0])

    else:
        values = []
        for col_name in df_res.columns:
            col = df_res[col_name].astype(str)
            n_dec = cntx.varidx.get_precision()
            for i in range(len(col)):
                try:
                    col[i] = str("{:." + str(n_dec) + "f}").format(float(col[i]))
                except ValueError:
                    pass
            values.append(col)
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df_res.columns),
                        line_color="white",
                        fill_color=cntx.col_sb_fill,
                        align="right"),
            cells=dict(values=values,
                       line_color="white",
                       fill_color="white",
                       align="right"))
        ])
        fig.data[0]["columnwidth"] = [200] + [100] * (len(df_res.columns) - 1)
        fig.update_layout(
            font=dict(
                size=15
            )
        )
        res = fig

    return res


def get_ref_val(
    cntx: def_context.Context
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the reference value.

    Parameters
    ----------
    cntx : def_context.Context
        Context.
        
    Returns
    -------
    str
        Reference value and unit.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    cntx_tbl = cntx.copy()
    cntx_tbl.view = def_view.View(def_view.code_tbl)
    df = dash_utils.load_data(cntx_tbl)
    
    # Extract value.
    val = df[df["rcp"] == def_rcp.rcp_ref]["val"][0]
    if cntx.varidx.get_precision == 0:
        val = int(val)
    val = str(val)
    unit = cntx.varidx.get_unit()
    if unit != "°C":
        val += " "
    
    return val + unit


def gen_map(
    cntx: def_context.Context,
    df: pd.DataFrame,
    z_range: List[float]
) -> Union[any, plt.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a heat map using matplotlib.

    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe (with 2 dimensions: longitude and latitude).
    z_range : List[float]
        Range of values to consider in colorbar.

    Returns
    -------
    Union[any, plt.Figure]
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Find minimum and maximum values (consider all relevant cases).
    z_min = z_range[0]
    z_max = z_range[1]

    # Number of clusters.
    n_cluster = 10 if cntx.opt_map_discrete else 256
    if (z_min < 0) and (z_max > 0):
        n_cluster = n_cluster * 2

    # Adjust minimum and maximum values so that zero is attributed the intermediate color in a scale or
    # use only the positive or negative side of the color scale if the other part is not required.
    if (z_min < 0) and (z_max > 0):
        v_max_abs = max(abs(z_min), abs(z_max))
        v_range = [-v_max_abs, v_max_abs]
    else:
        v_range = [z_min, z_max]

    # Maximum number of decimal places for colorbar ticks.
    n_dec_max = 4

    # Calculate ticks.
    ticks = None
    tick_labels = None
    if cntx.opt_map_discrete:
        ticks = []
        for i in range(n_cluster + 1):
            tick = i / float(n_cluster) * (v_range[1] - v_range[0]) + v_range[0]
            ticks.append(tick)

        # Adjust tick precision.
        tick_labels = adjust_precision(ticks, n_dec_max)

    # Adjust minimum and maximum values.
    if ticks is not None:
        v_range = [ticks[0], ticks[n_cluster]]

    # Build color map (custom or matplotlib).
    cmap_name = get_cmap_name(cntx, z_min, z_max)
    hex_l = get_hex_l(cmap_name)
    if hex_l is not None:
        cmap = get_cmap(cmap_name, hex_l, n_cluster)
    else:
        cmap = plt.cm.get_cmap(cmap_name, n_cluster)

    # Load locations.
    p = cntx.p_locations
    df_loc = None
    if os.path.exists(p):
        df_loc = pd.read_csv(p)

    # Generate map.
    if cntx.lib.get_code() == def_lib.mode_hv:
        fig = gen_map_hv(cntx, df, df_loc, v_range, cmap, ticks, tick_labels)
    else:
        fig = gen_map_mat(cntx, df, df_loc, v_range, cmap, ticks, tick_labels)

    return fig


def gen_map_hv(
    cntx: def_context.Context,
    df: pd.DataFrame,
    df_loc: pd.DataFrame,
    v_range: List[float],
    cmap: plt.cm,
    ticks: List[float],
    tick_labels: List[str]
) -> any:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a heat map using matplotlib.

    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    df_loc : pd.DataFrame
        Dataframe.
    v_range : List[float]
        Minimum and maximum values in colorbar.
    cmap : plt.cm
        Color map.
    ticks : List[float]
        Ticks.
    tick_labels : List[str]
        Tick labels.

    Returns
    -------
    any
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs_labels      = 10
    fs_annotations = 8

    # Label.
    label = ("Δ" if cntx.delta else "") + cntx.varidx.get_label()

    # Generate mesh.
    df.rename(columns={cntx.varidx.get_name(): "Valeur", "longitude": "Longitude", "latitude": "Latitude"},
              inplace=True)
    heatmap = df.hvplot.heatmap(x="Longitude", y="Latitude", C="Valeur", aspect="equal").\
        opts(cmap=cmap, clim=(v_range[0], v_range[1]), clabel=label)

    # Adjust ticks.
    if cntx.opt_map_discrete:
        ticker = FixedTicker(ticks=ticks)
        ticks_dict = {ticks[i]: tick_labels[i] for i in range(len(ticks))}
        heatmap = heatmap.opts(colorbar_opts={"ticker": ticker, "major_label_overrides": ticks_dict})

    # Create region boundary.
    df_curve = dash_utils.load_geojson(cntx.p_bounds, "pandas")
    x_lim = (min(df_curve["longitude"]), max(df_curve["longitude"]))
    y_lim = (min(df_curve["latitude"]), max(df_curve["latitude"]))
    curve = df_curve.hvplot.line(x="longitude", y="latitude", color="black", alpha=0.7, xlim=x_lim, ylim=y_lim)

    # Create locations.
    points = None
    labels = None
    if (df_loc is not None) and (len(df_loc) > 0):
        df_loc.rename(columns={"longitude": "Longitude", "latitude": "Latitude", "desc": "Emplacement"}, inplace=True)
        points = df_loc.hvplot.points(x="Longitude", y="Latitude", color="black", hover_cols=["Emplacement"])
        labels = hv.Labels(data=df_loc, x="Longitude", y="Latitude", text="Emplacement").\
            opts(xoffset=0.05, yoffset=0.1, padding=0.2, text_color="black", text_align="left",
                 text_font_style="italic", text_font_size=str(fs_annotations) + "pt")

    # Combine layers.
    fig = (heatmap * curve)
    if points is not None:
        fig = fig * points * labels

    # Add legend.
    fig = fig.opts(height=400, width=740, xlabel="Longitude (°C)", ylabel="Latitude (°C)", fontsize=fs_labels)

    return fig


def gen_map_mat(
    cntx: def_context.Context,
    df: pd.DataFrame,
    df_loc: pd.DataFrame,
    v_range: List[float],
    cmap: plt.cm,
    ticks: List[float],
    tick_labels: List[str]
) -> plt.Figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a heat map using matplotlib.
    
    Parameters
    ----------
    cntx : def_context.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    df_loc : pd.DataFrame
        Dataframe.
    v_range : List[float]
        Minimum and maximum values in colorbar..
    cmap : plt.cm
        Color map.
    ticks : List[float]
        Ticks.
    tick_labels : List[str]
        Tick labels.

    Returns
    -------
    plt.Figure
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs            = 6 if cntx.code == def_context.code_streamlit else 10
    fs_labels     = fs
    fs_ticks      = fs
    fs_ticks_cbar = fs
    if cntx.delta:
        fs_ticks_cbar = fs_ticks_cbar - 1

    # Label.
    label = ("Δ" if cntx.delta else "") + cntx.varidx.get_label()

    # Initialize figure and axes.
    if def_context.code_streamlit in cntx.code:
        fig = plt.figure(figsize=(9, 4.45), dpi=cntx.dpi)
    else:
        fig = plt.figure(dpi=cntx.dpi)
        width = 10
        w_to_d_ratio = fig.get_figwidth() / fig.get_figheight()
        fig.set_figwidth(width)
        fig.set_figheight(width / w_to_d_ratio)
        plt.subplots_adjust(top=0.98, bottom=0.10, left=0.08, right=0.92, hspace=0.0, wspace=0.0)
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:], aspect="equal")

    # Convert to DataArray.
    df = pd.DataFrame(df, columns=["longitude", "latitude", cntx.varidx.get_code()])
    df = df.sort_values(by=["latitude", "longitude"])
    lat = list(set(df["latitude"]))
    lat.sort()
    lon = list(set(df["longitude"]))
    lon.sort()
    arr = np.reshape(list(df[cntx.varidx.get_code()]), (len(lat), len(lon)))
    da = xr.DataArray(data=arr, dims=["latitude", "longitude"], coords=[("latitude", lat), ("longitude", lon)])

    # Generate mesh.
    cbar_ax = make_axes_locatable(ax).append_axes("right", size="5%", pad=0.05)
    da.plot.pcolormesh(cbar_ax=cbar_ax, add_colorbar=True, add_labels=True,
                       ax=ax, cbar_kwargs=dict(orientation="vertical", pad=0.05, label=label, ticks=ticks),
                       cmap=cmap, vmin=v_range[0], vmax=v_range[1])

    # Format.
    ax.set_xlabel("Longitude (º)", fontsize=fs_labels)
    ax.set_ylabel("Latitude (º)", fontsize=fs_labels)
    ax.tick_params(axis="x", labelsize=fs_ticks, length=5, rotation=90)
    ax.tick_params(axis="y", labelsize=fs_ticks, length=5)
    ax.set_xticks(ax.get_xticks(), minor=True)
    ax.set_yticks(ax.get_yticks(), minor=True)
    if cntx.opt_map_discrete:
        cbar_ax.set_yticklabels(tick_labels)
    cbar_ax.set_ylabel(label, fontsize=fs_labels)
    cbar_ax.tick_params(labelsize=fs_ticks_cbar, length=0)

    # Draw region boundary.
    draw_region_boundary(cntx, ax)

    # Draw locations.
    if df_loc is not None:
        ax.scatter(df_loc["longitude"], df_loc["latitude"], c="black", s=10)
        for i in range(len(df_loc)):
            offset = 0.05
            ax.text(df_loc["longitude"][i] + offset, df_loc["latitude"][i] + offset, df_loc["desc"][i],
                    fontdict=dict(color="black", size=fs_labels, style="italic"))

    plt.close(fig)
    
    return fig


def get_cmap_name(
    cntx: def_context.Context,
    z_min: float,
    z_max: float
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get colour map name.

    Parameters
    ----------
    cntx : def_context.Context
        Context.
    z_min : float
        Minimum value.
    z_max : float
        Maximum value.

    Returns
    -------
    str
        Colour map name.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Determine color scale index.
    is_wind_var = cntx.varidx.get_code() in [vi.v_uas, vi.v_vas, vi.v_sfcwindmax]
    if (not cntx.delta) and (not is_wind_var):
        cmap_idx = 0
    elif (z_min < 0) and (z_max > 0):
        cmap_idx = 1
    elif (z_min < 0) and (z_max < 0):
        cmap_idx = 2
    else:
        cmap_idx = 3

    # Temperature-related.
    if cntx.varidx.get_code() in \
        [vi.v_tas, vi.v_tasmin, vi.v_tasmax, vi.i_etr, vi.i_tgg,
         vi.i_tng, vi.i_tnx, vi.i_txx, vi.i_txg]:
        cmap_name = cntx.opt_map_col_temp_var[cmap_idx]
    elif cntx.varidx.get_code() in \
        [vi.i_tx_days_above, vi.i_heat_wave_max_length, vi.i_heat_wave_total_length,
         vi.i_hot_spell_frequency, vi.i_hot_spell_max_length, vi.i_tropical_nights,
         vi.i_tx90p, vi.i_wsdi]:
        cmap_name = cntx.opt_map_col_temp_idx_1[cmap_idx]
    elif cntx.varidx.get_code() in [vi.i_tn_days_below, vi.i_tng_months_below]:
        cmap_name = cntx.opt_map_col_temp_idx_2[cmap_idx]

    # Precipitation-related.
    elif cntx.varidx.get_code() in \
        [vi.v_pr, vi.i_prcptot, vi.i_rx1day, vi.i_rx5day, vi.i_sdii,
         vi.i_rain_season_prcptot]:
        cmap_name = cntx.opt_map_col_prec_var[cmap_idx]
    elif cntx.varidx.get_code() in \
        [vi.i_cwd, vi.i_r10mm, vi.i_r20mm, vi.i_wet_days, vi.i_rain_season_length,
         vi.i_rnnmm]:
        cmap_name = cntx.opt_map_col_prec_idx_1[cmap_idx]
    elif cntx.varidx.get_code() in \
        [vi.i_cdd, vi.i_dry_days, vi.i_drought_code,
         vi.i_dry_spell_total_length]:
        cmap_name = cntx.opt_map_col_prec_idx_2[cmap_idx]
    elif cntx.varidx.get_code() in [vi.i_rain_season_start, vi.i_rain_season_end]:
        cmap_name = cntx.opt_map_col_prec_idx_3[cmap_idx]

    # Wind-related.
    elif cntx.varidx.get_code() in [vi.v_uas, vi.v_vas, vi.v_sfcwindmax]:
        cmap_name = cntx.opt_map_col_wind_var[cmap_idx]
    elif cntx.varidx.get_code() in [vi.i_wg_days_above, vi.i_wx_days_above]:
        cmap_name = cntx.opt_map_col_wind_idx_1[cmap_idx]

    # Default values.
    else:
        cmap_name = cntx.opt_map_col_default[cmap_idx]

    return cmap_name


def get_hex_l(
    name: str
) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the list of HEX color codes associated with a color map.

    Parameters
    ----------
    name : str
        Name of a color map.

    Returns
    -------
    List[str]
        List of HEX color codes.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Custom color maps (not in matplotlib). The order assumes a vertical color bar.
    hex_wh  = "#ffffff"  # White.
    hex_gy  = "#808080"  # Grey.
    hex_gr  = "#008000"  # Green.
    hex_yl  = "#ffffcc"  # Yellow.
    hex_or  = "#f97306"  # Orange.
    hex_br  = "#662506"  # Brown.
    hex_rd  = "#ff0000"  # Red.
    hex_pi  = "#ffc0cb"  # Pink.
    hex_pu  = "#800080"  # Purple.
    hex_bu  = "#0000ff"  # Blue.
    hex_lbu = "#7bc8f6"  # Light blue.
    hex_lbr = "#d2b48c"  # Light brown.
    hex_sa  = "#a52a2a"  # Salmon.
    hex_tu  = "#008080"  # Turquoise.

    code_hex_l = {
        "Pinks": [hex_wh, hex_pi],
        "PiPu": [hex_pi, hex_wh, hex_pu],
        "Browns": [hex_wh, hex_br],
        "YlBr": [hex_yl, hex_br],
        "BrYlGr": [hex_br, hex_yl, hex_gr],
        "YlGr": [hex_yl, hex_gr],
        "BrWhGr": [hex_br, hex_wh, hex_gr],
        "TuYlSa": [hex_tu, hex_yl, hex_sa],
        "YlTu": [hex_yl, hex_tu],
        "YlSa": [hex_yl, hex_sa],
        "LBuWhLBr": [hex_lbu, hex_wh, hex_lbr],
        "LBlues": [hex_wh, hex_lbu],
        "BuYlRd": [hex_bu, hex_yl, hex_rd],
        "LBrowns": [hex_wh, hex_lbr],
        "LBuYlLBr": [hex_lbu, hex_yl, hex_lbr],
        "YlLBu": [hex_yl, hex_lbu],
        "YlLBr": [hex_yl, hex_lbr],
        "YlBu": [hex_yl, hex_bu],
        "Turquoises": [hex_wh, hex_tu],
        "PuYlOr": [hex_pu, hex_yl, hex_or],
        "YlOrRd": [hex_yl, hex_or, hex_rd],
        "YlOr": [hex_yl, hex_or],
        "YlPu": [hex_yl, hex_pu],
        "GyYlRd": [hex_gy, hex_yl, hex_rd],
        "YlGy": [hex_yl, hex_gy],
        "YlRd": [hex_yl, hex_rd],
        "GyWhRd": [hex_gy, hex_wh, hex_rd]}

    hex_l = None
    if name in list(code_hex_l.keys()):
        hex_l = code_hex_l[name]

    return hex_l


def get_cmap(
    cmap_name: str,
    hex_l: [str],
    n_cluster: int
):
    """
    --------------------------------------------------------------------------------------------------------------------
    Create a color map that can be used in heat map figures.

    If pos_l is not provided, color map graduates linearly between each color in hex_l.
    If pos_l is provided, each color in hex_l is mapped to the respective location in pos_l.

    Parameters
    ----------
    cmap_name : str
        Name of a color map.
    hex_l: [str]
        List of hex code strings.
    n_cluster: int
        Number of clusters.

    Returns
    -------
        Color map.
    --------------------------------------------------------------------------------------------------------------------
    """

    # List of positions.
    if len(hex_l) == 2:
        pos_l = [0.0, 1.0]
    else:
        pos_l = [0.0, 0.5, 1.0]

    # Reverse hex list.
    if "_r" in cmap_name:
        hex_l.reverse()

    # Build colour map.
    rgb_l = [rgb_to_dec(hex_to_rgb(i)) for i in hex_l]
    if pos_l:
        pass
    else:
        pos_l = list(np.linspace(0, 1, len(rgb_l)))
    cdict = dict()
    for num, col in enumerate(["red", "green", "blue"]):
        col_l = [[pos_l[i], rgb_l[i][num], rgb_l[i][num]] for i in range(len(pos_l))]
        cdict[col] = col_l
    cmap = colors.LinearSegmentedColormap("custom_cmap", segmentdata=cdict, N=n_cluster)

    return cmap


def adjust_precision(
    vals: [float],
    n_dec_max: int = 4
) -> List[str]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Adjust the precision of float values in a list so that each value is different than the following one.

    Parameters
    ----------
    vals : [float]
        List of values.
    n_dec_max : int, optional
        Maximum number of decimal places.
    
    Returns
    -------
    str
        Value with adjusted precision.
    --------------------------------------------------------------------------------------------------------------------
    """

    str_vals = []

    # Loop through potential numbers of decimal places.
    for n_dec in range(0, n_dec_max):

        # Loop through values.
        unique_vals = True
        str_vals = []
        for i in range(len(vals)):
            val = vals[i]
            if n_dec == 0:
                if not np.isnan(float(val)):
                    str_val = str(int(round(val, n_dec)))
                else:
                    str_val = str(val)
                str_vals.append(str_val)
            else:
                str_val = str(round(val, n_dec))
                str_vals.append(str("{:." + str(n_dec) + "f}").format(float(str_val)))

            # Two consecutive rounded values are equal.
            if i > 0:
                if str_vals[i - 1] == str_vals[i]:
                    unique_vals = False

        # Stop loop if all values are unique.
        if unique_vals or (n_dec == n_dec_max):
            break

    return str_vals


def draw_region_boundary(
    cntx: def_context.Context,
    ax: plt.axes
) -> plt.axes:

    """
    --------------------------------------------------------------------------------------------------------------------
    Draw region boundary.

    Parameters
    ----------
    cntx: def_context.Context
        Context.
    ax : plt.axes
        Plots axes.
    --------------------------------------------------------------------------------------------------------------------
    """

    def _set_plot_extent(_ax, _vertices):

        # Extract limits.
        x_min = x_max = y_min = y_max = None
        for i in range(len(_vertices)):
            x_i = _vertices[i][0]
            y_i = _vertices[i][1]
            if i == 0:
                x_min = x_max = x_i
                y_min = y_max = y_i
            else:
                x_min = min(x_i, x_min)
                x_max = max(x_i, x_max)
                y_min = min(y_i, y_min)
                y_max = max(y_i, y_max)

        # Set the graph axes to the feature extents
        _ax.set_xlim(x_min, x_max)
        _ax.set_ylim(y_min, y_max)
        
        return _ax

    def _plot_feature(_coordinates, _ax):
        
        _patch = PolygonPatch({"type": "Polygon", "coordinates": _coordinates},
                              fill=False, ec="black", alpha=0.75, zorder=2)
        _ax.add_patch(_patch)
        
        return _ax

    # Load geojson file.
    vertices, coordinates = dash_utils.load_geojson(cntx.p_bounds, "vertices")

    # Draw feature.
    ax_new = ax
    ax_new = _set_plot_extent(ax_new, vertices)
    ax_new = _plot_feature(coordinates, ax_new)
    
    return ax_new


def hex_to_rgb(
    value: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Converts hex to RGB colors

    Parameters
    ----------
    value: str
        String of 6 characters representing a hex color.

    Returns
    -------
        list of 3 RGB values
    --------------------------------------------------------------------------------------------------------------------
    """

    value = value.strip("#")
    lv = len(value)

    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(
    value: [int]
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Converts RGB to decimal colors (i.e. divides each value by 256)

    Parameters
    ----------
    value: [int]
        List of 3 RGB values.

    Returns
    -------
        List of 3 decimal values.
    --------------------------------------------------------------------------------------------------------------------
    """

    return [v/256 for v in value]


def gen_cycle_ms(
    cntx: def_context.Context,
    df: pd.DataFrame
) -> Union[any, plt.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a boxplot of monthly values.

    Parameters:
    ----------
    cntx: def_context.Context
        Context.
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    Union[any, plt.Figure]
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.lib.get_code() == def_lib.mode_hv:
        fig = gen_cycle_ms_hv(cntx, df)
    else:
        fig = gen_cycle_ms_mat(cntx, df)

    return fig


def gen_cycle_ms_hv(
    cntx: def_context.Context,
    df: pd.DataFrame
) -> any:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a boxplot of monthly values using hvplot.

    Parameters:
    ----------
    cntx: def_context.Context
        Context.
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    any
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Collect data.
    col_year = []
    col_month = []
    col_val = []
    for m in range(1, 13):
        col_year += list(df["year"])
        col_month += [m] * len(df)
        col_val += list(df[str(m)])

    # Translation between month number and string.
    ticks = list(range(1, 13))
    tick_labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    ticks_dict = {ticks[i]: tick_labels[i] for i in range(len(ticks))}

    # Prepare the dataframe that will be used in the plot.
    df = pd.DataFrame()
    df["Année"] = col_year
    df["Mois"] = col_month
    for i in range(len(df)):
        df.iloc[i, 1] = ticks_dict[df.iloc[i, 1]]
    df["Valeur"] = col_val

    # Generate plot.
    fig = df.hvplot.box(y="Valeur", by="Mois", height=375, width=730, legend=False,
                        box_fill_color="white", hover_cols=["Mois", "Valeur"]).\
        opts(tools=["hover"], ylabel=cntx.varidx.get_label())

    return fig


def gen_cycle_ms_mat(
    cntx: def_context.Context,
    df: pd.DataFrame
) -> plt.Figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a boxplot of monthly values using matplotlib.

    Parameters:
    ----------
    cntx: def_context.Context
        Context.
    df: pd.DataFrame
        Dataframe.
        
    Returns
    -------
    plt.Figure
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Collect data.
    data = []
    for m in range(1, 13):
        data.append(df[str(m)])

    # Font size.
    fs = 10
    fs_axes = fs

    # Draw.
    height = 5.45 if cntx.code == def_context.code_streamlit else 5.15
    fig = plt.figure(figsize=(9.95, height), dpi=cntx.dpi)
    plt.subplots_adjust(top=0.99, bottom=0.13, left=0.08, right=0.98, hspace=0.10, wspace=0.10)
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:])
    bp = ax.boxplot(data, showfliers=False)

    # Format.
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
               ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"], rotation=0)
    plt.xlabel("Mois", fontsize=fs_axes)
    plt.ylabel(cntx.varidx.get_label(), fontsize=fs_axes)
    plt.setp(bp["medians"], color="black")
    plt.tick_params(axis="x", labelsize=fs_axes)
    plt.tick_params(axis="y", labelsize=fs_axes)

    # Close plot.
    plt.close(fig)

    return fig


def gen_cycle_d(
    cntx: def_context.Context,
    df: pd.DataFrame
) -> Union[any, plt.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a time series of daily values.

    Parameters
    ----------
    cntx: def_context.Context
        Context.
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    Union[any, plt.Figure]
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.lib.get_code() == def_lib.mode_hv:
        fig = gen_cycle_d_hv(cntx, df)
    else:
        fig = gen_cycle_d_mat(cntx, df)

    return fig


def gen_cycle_d_hv(
    cntx: def_context.Context,
    df: pd.DataFrame
) -> plt.Figure:
    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a time series of daily values using hvplot

    Parameters
    ----------
    cntx: def_context.Context
        Context.
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    plt.Figure
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Rename columns.
    df.rename(columns={"day": "Jour", "mean": "Moyenne", "min": "Minimum", "max": "Maximum"}, inplace=True)

    # Draw area.
    area = df.hvplot.area(x="Jour", y="Minimum", y2="Maximum",
                          color="darkgrey", alpha=0.3, line_alpha=0, xlabel="Jour", ylabel=cntx.varidx.get_label())

    # Draw curve.
    tooltip = ["Jour", "Minimum", "Moyenne", "Maximum"]
    curve = df.hvplot.line(x="Jour", y="Moyenne", color="black", alpha=0.7, hover_cols=tooltip)

    # Combine components.
    plot = area * curve

    # Add legend.
    plot = plot.opts(legend_position="top_left", legend_opts={"click_policy": "hide", "orientation": "horizontal"},
                     frame_height=300, frame_width=645, border_line_alpha=0.0, background_fill_alpha=0.0)

    return plot

    
def gen_cycle_d_mat(
    cntx: def_context.Context,
    df: pd.DataFrame,
    plt_type: Optional[int] = 1
) -> Union[plt.Figure, None]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a time series of daily values using matplotlib.

    Parameters
    ----------
    cntx: def_context.Context
        Context.
    df: pd.DataFrame
        Dataframe.
    plt_type: Optional[int]
        Plot type {1=line, 2=bar}
        If the value
        
    Returns
    -------
    Union[plt.Figure, None]
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs = 10
    fs_axes = fs
    fs_legend = fs

    # Number of values on the x-axis.
    n = len(df)

    # Draw curve (mean values) and shadow (zone between minimum and maximum values).
    height = 5.45 if cntx.code == def_context.code_streamlit else 5.15
    fig, ax = plt.subplots(figsize=(9.95, height), dpi=cntx.dpi)
    plt.subplots_adjust(top=0.99, bottom=0.13, left=0.08, right=0.98, hspace=0.10, wspace=0.10)

    # Draw areas.
    ref_color = def_rcp.RCP(def_rcp.rcp_ref).get_color()
    rcp_color = "darkgrey"
    if plt_type == 1:
        ax.plot(range(1, n + 1), df["mean"], color=ref_color, alpha=1.0)
        ax.fill_between(np.array(range(1, n + 1)), df["mean"], df["max"], color=rcp_color, alpha=1.0)
        ax.fill_between(np.array(range(1, n + 1)), df["mean"], df["min"], color=rcp_color, alpha=1.0)
    else:
        bar_width = 1.0
        plt.bar(range(1, n + 1), df["max"], width=bar_width, color=rcp_color)
        plt.bar(range(1, n + 1), df["mean"], width=bar_width, color=rcp_color)
        plt.bar(range(1, n + 1), df["min"], width=bar_width, color="white")
        ax.plot(range(1, n + 1), df["mean"], color=ref_color, alpha=1.0)
        y_lim_lower = min(df["min"])
        y_lim_upper = max(df["max"])
        plt.ylim([y_lim_lower, y_lim_upper])

    # Format.
    plt.xlim([1, n])
    plt.xticks(np.arange(1, n + 1, 30))
    plt.xlabel("Jour", fontsize=fs_axes)
    plt.ylabel(cntx.varidx.get_label(), fontsize=fs_axes)
    plt.tick_params(axis="x", labelsize=fs_axes)
    plt.tick_params(axis="y", labelsize=fs_axes)

    # Format.
    plt.legend(["Valeur moyenne", "Étendue des valeurs"], fontsize=fs_legend)

    # Close plot.
    plt.close(fig)
    
    return fig
