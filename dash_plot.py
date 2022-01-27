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
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import altair as alt
import holoviews as hv
# Do not delete the following import statement (hvplot.pandas), even if it seems unused.
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

# Dashboard libraries.
import dash_statistics as stats
import dash_utils as du
import def_rcp
import def_sim
import def_stat
import def_varidx as vi
from def_constant import const as c
from def_context import cntx

alt.renderers.enable("default")
pn.extension("vega")
hv.extension("bokeh", logo=False)
pio.renderers.default = "iframe"

mode_rcp = "rcp"
mode_sim = "sim"


def gen_ts(
    df: pd.DataFrame,
    mode: Optional[str] = mode_rcp
) -> Union[alt.Chart, any, plt.figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series.
    
    Parameters
    ----------
    df: pd.DataFrame
        Dataframe.
    mode: Optional[str]
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    Union[alt.Chart, any, plt.figure] :
        Plot of time series.


    Logic related to line width (variable "line_alpha").

    plot | delta | simulation |   ref |   rcp
    -----+-------+------------+-------+------
    rcp  |   no  |      blank | thick | thick
    sim  |   no  |      blank | thick |  thin
    rcp  |  yes  |      blank |  thin | thick
    sim  |  yes  |      blank |  thin |  thin
    rcp  |   no  |  specified | thick | thick
    sim  |   no  |  specified | thick | thick
    rcp  |  yes  |  specified |  thin | thick
    sim  |  yes  |  specified |  thin | thick

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
    y_label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label

    # Assign zero to all years (not only to the refrence period).
    if cntx.delta.code == "True":
        df[c.ref] = 0

    # If there is a single row, add a second line to allow time series to work.
    if len(df) == 1:
        df = df.append(df.iloc[[0]], ignore_index=True)
        x_min = df["year"][1]
        x_max = x_min + 1
        df["year"][1] = x_max

    # Subset columns and rename columns.
    df_subset = df
    if mode == mode_sim:

        # RCP specified.
        rcp_code = cntx.rcp.code
        if rcp_code not in ["", c.rcpxx]:
            df_subset = df[["year", "ref"]]
            for column in df.columns:
                if rcp_code in column:
                    df_subset[column] = df[column]

        # Simulation specified.
        if cntx.sim.code not in ["", c.simxx]:
            df_subset = df[["year", "ref", cntx.sim.code]]

    # Combine RCPs.
    if (cntx.view.code == c.view_ts_bias) and (cntx.rcp.code in ["", c.rcpxx]) and (mode == mode_rcp):

        for stat in ["moy", c.stat_min, c.stat_max]:

            # Identify the columns associated with the current statistic.
            columns = []
            for column in df_subset.columns:
                if stat in column:
                    columns.append(column)

            # Calculate overall values.
            if stat == "moy":
                df_subset[c.rcpxx + "_" + stat] = df_subset[columns].mean(axis=1)
            elif stat == c.stat_min:
                df_subset[c.rcpxx + "_" + stat] = df_subset[columns].min(axis=1)
            elif stat == c.stat_max:
                df_subset[c.rcpxx + "_" + stat] = df_subset[columns].max(axis=1)

            # Delete columns.
            df_subset.drop(columns, axis=1, inplace=True)

    # Generate plot.
    if cntx.lib.code == c.lib_mat:
        ts = gen_ts_mat(df_subset, x_label, y_label, [x_min, x_max], [y_min, y_max], mode)
    elif cntx.lib.code == c.lib_hv:
        ts = gen_ts_hv(df_subset, x_label, y_label, [y_min, y_max], mode)
    else:
        ts = gen_ts_alt(df_subset, x_label, y_label, [y_min, y_max], mode)
        
    return ts


def gen_ts_alt(
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
    df: pd.DataFrame
        Dataframe.
    x_label: str
        X-label.
    y_label: str
        Y-label.
    y_range: List[str]
        Range of y_values to display [{y_min}, {y_max}].
        Dataframe.
    mode: str
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    alt.Chart :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Move reference RCP at the end of the list.
    if (cntx.view.code == c.view_ts) or (cntx.rcp.code not in ["", c.rcpxx]):
        rcps = cntx.rcps.copy()
        rcps.remove(c.ref, inplace=True)
    else:
        rcps = def_rcp.RCPs([c.rcpxx])
    rcps.add(def_rcp.RCP(c.ref), inplace=True)

    # Plot components.
    x_axis = alt.Axis(title=x_label, format="d")
    y_axis = alt.Axis(title=y_label, format="d")
    y_scale = alt.Scale(domain=y_range)
    color_l = rcps.color_l
    col_legend = alt.Legend(title="", orient="top-left", direction="horizontal", symbolType="stroke")
    if cntx.view.code == c.view_ts_bias:
        for i in range(len(color_l)):
            if color_l[i] != def_rcp.RCP(c.ref).color:
                color_l[i] = "darkgrey"
    col_scale = alt.Scale(range=color_l, domain=rcps.desc_l)

    # Add layers.
    plot = None
    for item in ["area", "curve"]:

        for rcp in rcps.items:

            cond_ts      = (cntx.view.code == c.view_ts) and (cntx.rcp.code not in ["", c.rcpxx])
            cond_ts_bias = (cntx.view.code == c.view_ts_bias) and (cntx.rcp.code != "")
            if ((item == "area") and (rcp.is_ref or (mode == mode_sim))) or \
               ((cond_ts or cond_ts_bias) and (rcp.code not in [cntx.rcp.code, c.ref])):
                continue

            rcp_desc = rcp.desc.replace(dict(def_rcp.code_props())[c.rcpxx][0], "Simulation(s)")

            # Subset columns.
            df_rcp = pd.DataFrame()
            df_rcp["Année"] = df["year"]
            df_rcp["Scénario"] = [rcp.desc] * len(df)
            if rcp.is_ref:
                df_rcp["Moy"] = df[c.ref]
            else:
                if mode == mode_rcp:
                    df_rcp["Min"] = df[rcp.code + "_" + c.stat_min]
                    df_rcp["Moy"] = df[rcp.code + "_moy"]
                    df_rcp["Max"] = df[rcp.code + "_" + c.stat_max]
                else:
                    for column in list(df.columns):
                        if (rcp.code in column) or ((rcp.code == c.rcpxx) and ("rcp" in column)):
                            df_rcp[column] = df[column]

            # Round values and set tooltip.
            n_dec = cntx.varidx.precision
            tooltip = []
            if "Moy" in df_rcp:
                column = "Moyenne"
                if ("Min" not in list(df_rcp.columns)) and ("Max" not in list(df_rcp.columns)):
                    column = "Valeur"
                df_rcp[column] = np.array(du.round_values(df_rcp["Moy"], n_dec)).astype(float)
                tooltip = [column]
            if "Min" in df_rcp:
                df_rcp["Minimum"] = np.array(du.round_values(df_rcp["Min"], n_dec)).astype(float)
                df_rcp["Maximum"] = np.array(du.round_values(df_rcp["Max"], n_dec)).astype(float)
                tooltip = ["Minimum", "Moyenne", "Maximum"]
            if mode == mode_sim:
                excl_l = ["Scénario", "Année", "Moy", "Min", "Max"]
                tooltip = [e for e in list(df_rcp.columns) if e not in excl_l]
                tooltip.sort()
            tooltip = ["Année", "Scénario"] + tooltip

            # Draw area.
            if (item == "area") and (mode == mode_rcp):
                area_alpha = 0.3
                area = alt.Chart(df_rcp).mark_area(opacity=area_alpha, text=rcp_desc).encode(
                    x=alt.X("Année", axis=x_axis),
                    y=alt.Y("Min", axis=y_axis, scale=y_scale),
                    y2="Max",
                    color=alt.Color("Scénario", scale=col_scale, legend=col_legend)
                )
                plot = area if plot is None else (plot + area)
            
            # Draw curve(s).
            elif item == "curve":

                # Line width (see comment in the header of 'gen_ts').
                if (rcp.is_ref and (cntx.delta.code == "True")) or \
                   ((not rcp.is_ref) and (mode == mode_sim) and (cntx.sim.code == "")):
                    line_alpha = 1.0
                else:
                    line_alpha = 2.0

                # Columns to plot.
                columns = []
                if "Valeur" in list(df_rcp.columns):
                    columns.append("Valeur")
                if ("Moy" in list(df_rcp.columns)) and ("Valeur" not in list(df_rcp.columns)):
                    columns.append("Moy")
                if mode == mode_sim:
                    for column in list(df_rcp.columns):
                        if ("Année" not in column) and ("Scénario" not in column):
                            columns.append(column)

                # Draw curves.
                for column in columns:
                    if rcp.is_ref:
                        curve = alt.Chart(df_rcp).\
                            mark_line(size=line_alpha, text=rcp_desc, color=rcp.color).encode(
                            x=alt.X("Année", axis=x_axis),
                            y=alt.Y(column, axis=y_axis, scale=y_scale),
                            color=alt.Color("Scénario", scale=col_scale, legend=col_legend),
                            tooltip=tooltip
                        ).interactive()
                    else:
                        curve = alt.Chart(df_rcp).mark_line(size=line_alpha, text=rcp_desc).encode(
                            x=alt.X("Année", axis=x_axis),
                            y=alt.Y(column, axis=y_axis, scale=y_scale),
                            color=alt.Color("Scénario", scale=col_scale, legend=col_legend),
                            tooltip=tooltip
                        ).interactive()
                    plot = curve if plot is None else (plot + curve)

    # Adjust size and title
    height = 362 if cntx.code == c.platform_streamlit else 300
    title = alt.TitleParams([plot_title(), plot_code()])
    plot = plot.configure_axis(grid=False).properties(height=height, width=650, title=title).\
        configure_title(offset=0, orient="top", anchor="start")

    return plot


def gen_ts_hv(
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
    df: pd.DataFrame
        Dataframe.
    x_label: str
        X-label.
    y_label: str
        Y-label.
    y_range: List[str]
        Range of y_values to display [{y_min}, {y_max}].
        Dataframe.
    mode: str
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    any :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Move reference RCP at the end of the list.
    if (cntx.view.code == c.view_ts) or (cntx.rcp.code not in ["", c.rcpxx]):
        rcps = cntx.rcps.copy()
        rcps.remove(c.ref, inplace=True)
    else:
        rcps = def_rcp.RCPs([c.rcpxx])
    rcps.add(def_rcp.RCP(c.ref), inplace=True)

    # Loop through RCPs.
    plot = None
    for item in ["area", "curve"]:

        for rcp in rcps.items:

            cond_ts      = (cntx.view.code == c.view_ts) and (cntx.rcp.code not in ["", c.rcpxx])
            cond_ts_bias = (cntx.view.code == c.view_ts_bias) and (cntx.rcp.code != "")
            if (item == "area") and (rcp.is_ref or (mode == mode_sim)) or \
               ((cond_ts or cond_ts_bias) and (rcp.code not in [cntx.rcp.code, c.ref])):
                continue

            # Color (area and curve).
            color = rcp.color if (cntx.view.code == c.view_ts) or (rcp.code == c.ref) else "darkgrey"

            # Subset and rename columns.
            df_rcp = pd.DataFrame()
            df_rcp["Année"] = df["year"]
            df_rcp["Scénario"] = [rcp.desc] * len(df_rcp)
            if rcp.is_ref:
                df_rcp["Moyenne"] = df[c.ref]
            else:
                if mode == mode_rcp:
                    if str(rcp.code + "_" + c.stat_min) in df.columns:
                        df_rcp["Minimum"] = df[str(rcp.code + "_" + c.stat_min)]
                    if str(rcp.code + "_moy") in df.columns:
                        df_rcp["Moyenne"] = df[str(rcp.code + "_moy")]
                    if str(rcp.code + "_" + c.stat_max) in df.columns:
                        df_rcp["Maximum"] = df[str(rcp.code + "_" + c.stat_max)]
                else:
                    for column in list(df.columns):
                        if (rcp.code in column) or ((rcp.code == c.rcpxx) and ("rcp" in column)):
                            df_rcp[def_sim.Sim(column).desc] = df[column]

            # Round values and set tooltip.
            n_dec = cntx.varidx.precision
            tooltip = []
            if "Moyenne" in df_rcp:
                column = "Moyenne"
                if ("Minimum" not in df_rcp.columns) and ("Maximum" not in df_rcp.columns):
                    column = "Valeur"
                df_rcp[column] = np.array(du.round_values(df_rcp["Moyenne"], n_dec)).astype(float)
                tooltip = [column]
            if "Minimum" in df_rcp:
                df_rcp["Minimum"] = np.array(du.round_values(df_rcp["Minimum"], n_dec)).astype(float)
                df_rcp["Maximum"] = np.array(du.round_values(df_rcp["Maximum"], n_dec)).astype(float)
                tooltip = ["Minimum", "Moyenne", "Maximum"]
            if mode == mode_sim:
                excl_l = ["Scénario", "Année", "Moyenne", "Minimum", "Maximum"]
                tooltip = [e for e in list(df_rcp.columns) if e not in excl_l]
                tooltip.sort()
            tooltip = ["Année", "Scénario"] + tooltip

            # Draw area.
            if item == "area":
                area_alpha = 0.3
                area = df_rcp.hvplot.area(x="Année", y="Minimum", y2="Maximum", ylim=y_range,
                                          color=color, alpha=area_alpha, line_alpha=0)
                plot = area if plot is None else plot * area

            # Draw curve(s).
            elif item == "curve":

                # Line width (see comment in the header of 'gen_ts').
                if (rcp.is_ref and (cntx.delta.code == "True")) or \
                   ((not rcp.is_ref) and (mode == mode_sim) and (cntx.sim.code == "")):
                    line_alpha = 0.3
                else:
                    line_alpha = 1.0

                # Columns to plot.
                columns = []
                if "Valeur" in df_rcp.columns:
                    columns.append("Valeur")
                if ("Moyenne" in df_rcp.columns) and ("Valeur" not in df_rcp.columns):
                    columns.append("Moyenne")
                if mode == mode_sim:
                    for column in list(df_rcp.columns):
                        if ("Année" not in column) and ("Scénario" not in column):
                            columns.append(column)

                # Draw curves.
                for column in columns:
                    desc = rcp.desc.replace(dict(def_rcp.code_props())[c.rcpxx][0], "Simulation(s)")
                    curve = df_rcp.hvplot.line(x="Année", y=column, ylim=y_range, color=color,
                                               line_alpha=line_alpha, label=desc, hover_cols=tooltip)
                    plot = curve if plot is None else plot * curve

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plot = plot.opts(hv.opts.Overlay(title=title))

    # Adjust size and add legend.
    plot = plot.opts(legend_position="top_left", legend_opts={"click_policy": "hide", "orientation": "horizontal"},
                     frame_height=300, frame_width=645, border_line_alpha=0.0, background_fill_alpha=0.0,
                     xlabel=x_label, ylabel=y_label)

    return plot


def gen_ts_mat(
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
    df: pd.DataFrame
        Dataframe.
    x_label: str
        X-label.
    y_label: str
        Y-label.
    x_range: List[float]
        Range of x_values to display [{x_min}, {x_max}].
    y_range: List[float]
        Range of y_values to display [{y_min}, {y_max}].
    mode: str
        If mode == mode_rcp: show curves and envelopes.
        If mode == mode_sim: show curves only.

    Returns
    -------
    plt.Figure :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs        = 9 if cntx.code == c.platform_streamlit else 10
    fs_title  = fs + 1
    fs_labels = fs
    fs_ticks  = fs

    # Initialize figure and axes.
    if c.platform_streamlit in cntx.code:
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
    if (cntx.view.code == c.view_ts) or (cntx.rcp.code not in ["", c.rcpxx]):
        rcps = cntx.rcps.copy()
        rcps.remove(c.ref, inplace=True)
    else:
        rcps = def_rcp.RCPs([c.rcpxx])
    rcps.add(def_rcp.RCP(c.ref), inplace=True)

    # Loop through RCPs.
    leg_labels = []
    leg_lines = []
    for rcp in rcps.items:

        cond_ts = (cntx.view.code == c.view_ts) and (cntx.rcp.code not in ["", c.rcpxx])
        cond_ts_bias = (cntx.view.code == c.view_ts_bias) and (cntx.rcp.code != "")
        if (cond_ts or cond_ts_bias) and (rcp.code not in [cntx.rcp.code, c.ref]):
            continue

        # Color (area and curve).
        color = rcp.color if (cntx.view.code == c.view_ts) or (rcp.code == c.ref) else "darkgrey"

        # Subset and rename columns.
        df_year = df.year
        df_rcp = pd.DataFrame()
        if rcp.is_ref:
            df_rcp["Moy"] = df[c.ref]
        else:
            if mode == mode_rcp:
                if str(rcp.code + "_moy") in df.columns:
                    df_rcp["Moy"] = df[str(rcp.code + "_moy")]
                if str(rcp.code + "_" + c.stat_min) in df.columns:
                    df_rcp["Min"] = df[str(rcp.code + "_" + c.stat_min)]
                if str(rcp.code + "_" + c.stat_max) in df.columns:
                    df_rcp["Max"] = df[str(rcp.code + "_" + c.stat_max)]
            else:
                for column in df.columns:
                    if (rcp.code in column) or ((rcp.code == c.rcpxx) and ("rcp" in column)):
                        df_rcp[def_sim.Sim(column).desc] = df[column]

        # Skip if no data is available for this RCP.
        if len(df_rcp) == 0:
            continue

        # Opacity of area
        area_alpha = 0.3

        # Line width (see comment in the header of 'gen_ts').
        if (rcp.is_ref and (cntx.delta.code == "True")) or \
           ((not rcp.is_ref) and (mode == mode_sim) and (cntx.sim.code == "")):
            line_alpha = 0.3
        else:
            line_alpha = 1.0

        # Draw area and curves.
        if rcp.is_ref:
            ax.plot(df_year, df_rcp, color=color, alpha=line_alpha)
        else:
            if mode == mode_rcp:
                ax.plot(df_year, df_rcp["Moy"], color=color, alpha=line_alpha)
                ax.fill_between(np.array(df_year), df_rcp["Min"], df_rcp["Max"], color=color,
                                alpha=area_alpha)
            else:
                for i in range(len(df_rcp.columns)):
                    ax.plot(df_year, df_rcp[df_rcp.columns[i]], color=color, alpha=line_alpha)
        
        # Collect legend label and line.
        desc = rcp.desc.replace(dict(def_rcp.code_props())[c.rcpxx][0], "Simulation(s)")
        leg_labels.append(desc)
        leg_lines.append(Line2D([0], [0], color=color, lw=2))

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plt.title(title, loc="left", fontweight="bold", fontsize=fs_title)

    # Legend.
    ax.legend(leg_lines, leg_labels, loc="upper left", ncol=len(leg_labels), mode="expland", frameon=False,
              fontsize=fs_labels)

    plt.close(fig)
    
    return fig


def gen_tbl(
) -> Union[pd.DataFrame, go.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a table.

    Returns
    -------
    Union[pd.DataFrame, go.Figure] :
        Dataframe or figure.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    df = pd.DataFrame(du.load_data())

    # List of statistics (in a column).
    stat_l, stat_desc_l = [], []
    for code in list(dict(def_stat.code_desc()).keys()):
        if code in [c.stat_min, c.stat_max, c.stat_mean]:
            stat_l.append([code, -1])
        elif code == "q" + cntx.project.quantiles_as_str[0]:
            stat_l.append(["quantile", cntx.project.quantiles[0]])
        elif code == "q" + cntx.project.quantiles_as_str[1]:
            stat_l.append(["quantile", cntx.project.quantiles[1]])
        else:
            stat_l.append(["quantile", 0.5])
        stat_desc_l.append(def_stat.code_desc()[code])

    # Initialize resulting dataframe.
    df_res = pd.DataFrame()
    df_res["Statistique"] = stat_desc_l

    # Loop through RCPs.
    columns = []
    for rcp in cntx.rcps.items:

        if rcp.is_ref:
            continue

        # Extract delta.
        delta = 0.0
        if cntx.delta.code == "True":
            delta = float(df[df["rcp"] == c.ref]["val"])

        # Extract statistics.
        vals = []
        for stat in stat_l:
            df_cell = float(df[(df["rcp"] == rcp.code) &
                               (df["hor"] == cntx.hor.code) &
                               (df["stat"] == stat[0]) &
                               (df["q"] == stat[1])]["val"])
            val = df_cell - delta
            vals.append(val)
        df_res[rcp.code] = vals

        # Adjust precision.
        n_dec = cntx.varidx.precision
        if n_dec == 0:
            df_res[rcp.code] = df_res[rcp.code].astype(int)
        else:
            for i in range(len(df_res)):
                try:
                    df_res[rcp.code] = str("{:." + str(n_dec) + "f}").format(float(df_res[rcp.code][i]))
                except ValueError:
                    pass

        columns.append(rcp.desc)

    df_res.columns = [df_res.columns[0]] + columns

    # Add units.
    for column in df_res.columns[1:]:
        df_res[column] = df_res[column].astype(str)
        df_res[column] += (" " if cntx.varidx.unit != "°C" else "") + cntx.varidx.unit

    # Title.
    title = "<b>" + str(plot_title()) + "<br>" + str(plot_code()) + "</b>"

    # In Jupyter Notebook, a dataframe appears nicely.
    if cntx.code == c.platform_jupyter:
        res = df_res.set_index(df_res.columns[0])

    # In Streamlit, a table needs to be formatted.
    else:
        values = []
        for col_name in df_res.columns:
            values.append(df_res[col_name])
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
        fig.update_layout(
            font=dict(size=15),
            width=700,
            height=180,
            margin=go.layout.Margin(l=0, r=0, b=0, t=50),
            title_text=title,
            title_x=0,
            title_font=dict(size=15)
        )
        res = fig

    return res


def gen_map(
    df: pd.DataFrame,
    z_range: List[float]
) -> Union[any, plt.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a heat map using matplotlib.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe (with 2 dimensions: longitude and latitude).
    z_range: List[float]
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
    tick_labels = []
    if cntx.opt_map_discrete:
        ticks = []
        for i in range(n_cluster + 1):
            tick = i / float(n_cluster) * (v_range[1] - v_range[0]) + v_range[0]
            ticks.append(tick)

        # Adjust tick precision.
        tick_labels = adjust_precision(ticks, n_dec_max=n_dec_max, output_type="str")

    # Adjust minimum and maximum values.
    if ticks is not None:
        v_range = [ticks[0], ticks[n_cluster]]

    # Build color map (custom or matplotlib).
    cmap_name = str(get_cmap_name(z_min, z_max))
    hex_l = get_hex_l(cmap_name)
    if hex_l is not None:
        cmap = get_cmap(cmap_name, hex_l, n_cluster)
    else:
        cmap = plt.cm.get_cmap(cmap_name, n_cluster)

    # Generate map.
    if cntx.lib.code == c.lib_hv:
        fig = gen_map_hv(df, cntx.opt_map_locations, v_range, cmap, ticks, tick_labels)
    else:
        fig = gen_map_mat(df, cntx.opt_map_locations, v_range, cmap, ticks, tick_labels)

    return fig


def gen_map_hv(
    df: pd.DataFrame,
    df_loc: pd.DataFrame,
    v_range: List[float],
    cmap: plt.cm,
    ticks: List[float],
    tick_labels: List[str]
) -> any:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a heat map using hvplot.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe.
    df_loc: pd.DataFrame
        Dataframe.
    v_range: List[float]
        Minimum and maximum values in colorbar.
    cmap: plt.cm
        Color map.
    ticks: List[float]
        Ticks.
    tick_labels: List[str]
        Tick labels.

    Returns
    -------
    any
        Plot.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs_labels      = 10
    fs_annotations = 8

    # Label.
    label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label

    # Generate mesh.
    df.rename(columns={cntx.varidx.name: "Valeur", "longitude": "Longitude", "latitude": "Latitude"}, inplace=True)
    heatmap = df.hvplot.heatmap(x="Longitude", y="Latitude", C="Valeur", aspect="equal").\
        opts(cmap=cmap, clim=(v_range[0], v_range[1]), clabel=label)

    # Adjust ticks.
    if cntx.opt_map_discrete:
        ticker = FixedTicker(ticks=ticks)
        ticks_dict = {ticks[i]: tick_labels[i] for i in range(len(ticks))}
        heatmap = heatmap.opts(colorbar_opts={"ticker": ticker, "major_label_overrides": ticks_dict})

    # Create region boundary.
    bounds = None
    if (cntx.p_bounds != "") and os.path.exists(cntx.p_bounds):
        df_curve = pd.DataFrame(du.load_geojson(cntx.p_bounds, "pandas"))
        x_lim = (min(df_curve["longitude"]), max(df_curve["longitude"]))
        y_lim = (min(df_curve["latitude"]), max(df_curve["latitude"]))
        bounds = df_curve.hvplot.line(x="longitude", y="latitude", color="black", alpha=0.7, xlim=x_lim, ylim=y_lim)

    # Create locations.
    points = None
    labels = None
    if (df_loc is not None) and (len(df_loc) > 0):
        df_loc = df_loc.copy()
        df_loc.rename(columns={"longitude": "Longitude", "latitude": "Latitude", "desc": "Emplacement"}, inplace=True)
        points = df_loc.hvplot.points(x="Longitude", y="Latitude", color="black", hover_cols=["Emplacement"])
        labels = hv.Labels(data=df_loc, x="Longitude", y="Latitude", text="Emplacement").\
            opts(xoffset=0.05, yoffset=0.1, padding=0.2, text_color="black", text_align="left",
                 text_font_style="italic", text_font_size=str(fs_annotations) + "pt")

    # Combine layers.
    plot = heatmap
    if bounds is not None:
        plot = plot * bounds
    if points is not None:
        plot = plot * points * labels

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plot = plot.opts(hv.opts.Overlay(title=title))

    # Add legend.
    plot = plot.opts(height=400, width=740, xlabel="Longitude (º)", ylabel="Latitude (º)", fontsize=fs_labels)

    return plot


def gen_map_mat(
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
    df: pd.DataFrame
        Dataframe.
    df_loc: pd.DataFrame
        Dataframe.
    v_range: List[float]
        Minimum and maximum values in colorbar..
    cmap: plt.cm
        Color map.
    ticks: List[float]
        Ticks.
    tick_labels: List[str]
        Tick labels.

    Returns
    -------
    plt.Figure
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Font size.
    fs            = 6 if cntx.code == c.platform_streamlit else 10
    fs_title      = fs + 2
    fs_labels     = fs
    fs_ticks      = fs
    fs_ticks_cbar = fs
    if cntx.delta.code == "True":
        fs_ticks_cbar = fs_ticks_cbar - 1

    # Label.
    label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label

    # Initialize figure and axes.
    if c.platform_streamlit in cntx.code:
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

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plt.title(title, loc="left", fontweight="bold", fontsize=fs_title)

    # Convert to DataArray.
    df = pd.DataFrame(df, columns=["longitude", "latitude", cntx.varidx.code])
    df = df.sort_values(by=["latitude", "longitude"])
    lat = list(set(df["latitude"]))
    lat.sort()
    lon = list(set(df["longitude"]))
    lon.sort()
    arr = np.reshape(list(df[cntx.varidx.code]), (len(lat), len(lon)))
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
    if (cntx.p_bounds != "") and os.path.exists(cntx.p_bounds):
        draw_region_boundary(ax)

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
    z_min: float,
    z_max: float
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get colour map name.

    Parameters
    ----------
    z_min: float
        Minimum value.
    z_max: float
        Maximum value.

    Returns
    -------
    str
        Colour map name.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Determine color scale index.
    is_wind_var = cntx.varidx.code in [c.v_uas, c.v_vas, c.v_sfcwindmax]
    if (cntx.delta.code == "False") and (not is_wind_var):
        cmap_idx = 0
    elif (z_min < 0) and (z_max > 0):
        cmap_idx = 1
    elif (z_min < 0) and (z_max < 0):
        cmap_idx = 2
    else:
        cmap_idx = 3

    # Temperature-related.
    if cntx.varidx.code in \
        [c.v_tas, c.v_tasmin, c.v_tasmax, c.i_etr, c.i_tgg, c.i_tng, c.i_tnx, c.i_txx, c.i_txg]:
        cmap_name = cntx.opt_map_col_temp_var[cmap_idx]
    elif cntx.varidx.code in \
        [c.i_tx_days_above, c.i_heat_wave_max_length, c.i_heat_wave_total_length, c.i_hot_spell_frequency,
         c.i_hot_spell_max_length, c.i_tropical_nights, c.i_tx90p, c.i_wsdi]:
        cmap_name = cntx.opt_map_col_temp_idx_1[cmap_idx]
    elif cntx.varidx.code in [c.i_tn_days_below, c.i_tng_months_below]:
        cmap_name = cntx.opt_map_col_temp_idx_2[cmap_idx]

    # Precipitation-related.
    elif cntx.varidx.code in [c.v_pr, c.i_prcptot, c.i_rx1day, c.i_rx5day, c.i_sdii, c.i_rain_season_prcptot]:
        cmap_name = cntx.opt_map_col_prec_var[cmap_idx]
    elif cntx.varidx.code in [c.i_cwd, c.i_r10mm, c.i_r20mm, c.i_wet_days, c.i_rain_season_length, c.i_rnnmm]:
        cmap_name = cntx.opt_map_col_prec_idx_1[cmap_idx]
    elif cntx.varidx.code in [c.i_cdd, c.i_dry_days, c.i_drought_code, c.i_dry_spell_total_length]:
        cmap_name = cntx.opt_map_col_prec_idx_2[cmap_idx]
    elif cntx.varidx.code in [c.i_rain_season_start, c.i_rain_season_end]:
        cmap_name = cntx.opt_map_col_prec_idx_3[cmap_idx]

    # Wind-related.
    elif cntx.varidx.code in [c.v_uas, c.v_vas, c.v_sfcwindmax]:
        cmap_name = cntx.opt_map_col_wind_var[cmap_idx]
    elif cntx.varidx.code in [c.i_wg_days_above, c.i_wx_days_above]:
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
    cmap_name: str
        Color map name.
    hex_l: [str]
        Hex code string list.
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

    return colors.LinearSegmentedColormap("custom_cmap", segmentdata=cdict, N=n_cluster)


def adjust_precision(
    val_l: List[float],
    n_dec_max: Optional[int] = 4,
    output_type: Optional[str] = "float"
) -> List[Union[int, float, str]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Adjust the precision of float values in a list so that each value is different than the following one.

    Parameters
    ----------
    val_l: List[float]
        List of values.
    n_dec_max: Optional[int]
        Maximum number of decimal places.
    output_type: Optional[str]
        Output type = {"int", "float", "str"}

    Returns
    -------
    List[Union[int, float, str]]
        Values with adjusted precision.
    --------------------------------------------------------------------------------------------------------------------
    """

    val_opt_l = []

    # Loop through potential numbers of decimal places.
    for n_dec in range(0, n_dec_max + 1):

        # Loop through values.
        unique_vals = True
        val_opt_l = []
        for i in range(len(val_l)):
            val_i = float(val_l[i])

            # Adjust precision.
            if n_dec == 0:
                if not np.isnan(float(val_i)):
                    val_i = str(int(round(val_i, n_dec)))
                else:
                    val_i = str(val_i)
            else:
                val_i = str("{:." + str(n_dec) + "f}").format(float(str(round(val_i, n_dec))))

            # Add value to list.
            val_opt_l.append(val_i)

            # Two consecutive rounded values are equal.
            if i > 0:
                if val_opt_l[i - 1] == val_opt_l[i]:
                    unique_vals = False

        # Stop loop if all values are unique.
        if unique_vals or (n_dec == n_dec_max):
            break

    # Convert values to output type if it's not numerical.
    val_new_l = []
    for i in range(len(val_l)):
        if output_type == "int":
            val_new_l.append(int(val_opt_l[i]))
        elif output_type == "float":
            val_new_l.append(float(val_opt_l[i]))
        else:
            val_new_l.append(val_opt_l[i])

    return val_new_l


def draw_region_boundary(
    ax: plt.axes
) -> plt.axes:

    """
    --------------------------------------------------------------------------------------------------------------------
    Draw region boundary.

    Parameters
    ----------
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

    def _plot_feature(_coords, _ax):
        
        _patch = PolygonPatch({"type": "Polygon", "coordinates": _coords},
                              fill=False, ec="black", alpha=0.75, zorder=2)
        _ax.add_patch(_patch)
        
        return _ax

    # Load geojson file.
    vertices, coords = du.load_geojson(cntx.p_bounds, "vertices")

    # Draw feature.
    ax_new = ax
    ax_new = _set_plot_extent(ax_new, vertices)
    ax_new = _plot_feature(coords, ax_new)
    
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
    df: pd.DataFrame
) -> Union[any, plt.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a boxplot of monthly values.

    Parameters:
    ----------
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    Union[any, plt.Figure]
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.lib.code == c.lib_hv:
        fig = gen_cycle_ms_hv(df)
    else:
        fig = gen_cycle_ms_mat(df)

    return fig


def gen_cycle_ms_hv(
    df: pd.DataFrame
) -> any:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a boxplot of monthly values using hvplot.

    Parameters:
    ----------
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    any
        Plot.
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

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())

    # Generate plot.
    y_label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label
    plot = df.hvplot.box(y="Valeur", by="Mois", height=375, width=730, legend=False, box_fill_color="white",
                         hover_cols=["Mois", "Valeur"]).opts(tools=["hover"], ylabel=y_label, title=title)

    return plot


def gen_cycle_ms_mat(
    df: pd.DataFrame
) -> plt.Figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a boxplot of monthly values using matplotlib.

    Parameters:
    ----------
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
    height = 5.45 if cntx.code == c.platform_streamlit else 5.15
    fig = plt.figure(figsize=(9.95, height), dpi=cntx.dpi)
    plt.subplots_adjust(top=0.99, bottom=0.13, left=0.08, right=0.98, hspace=0.10, wspace=0.10)
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:])
    bp = ax.boxplot(data, showfliers=False)

    # Format.
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
               ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"], rotation=0)
    plt.xlabel("Mois", fontsize=fs_axes)
    y_label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label
    plt.ylabel(y_label, fontsize=fs_axes)
    plt.setp(bp["medians"], color="black")
    plt.tick_params(axis="x", labelsize=fs_axes)
    plt.tick_params(axis="y", labelsize=fs_axes)

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plt.title(title, loc="left", fontweight="bold")

    # Close plot.
    plt.close(fig)

    return fig


def gen_cycle_d(
    df: pd.DataFrame
) -> Union[any, plt.Figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a time series of daily values.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe.

    Returns
    -------
    Union[any, plt.Figure]
        Figure.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.lib.code == c.lib_hv:
        fig = gen_cycle_d_hv(df)
    else:
        fig = gen_cycle_d_mat(df)

    return fig


def gen_cycle_d_hv(
    df: pd.DataFrame
) -> plt.Figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a time series of daily values using hvplot

    Parameters
    ----------
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
    y_label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label
    area = df.hvplot.area(x="Jour", y="Minimum", y2="Maximum",
                          color="darkgrey", alpha=0.3, line_alpha=0, xlabel="Jour", ylabel=y_label)

    # Draw curve.
    tooltip = ["Jour", "Minimum", "Moyenne", "Maximum"]
    curve = df.hvplot.line(x="Jour", y="Moyenne", color="black", alpha=0.7, hover_cols=tooltip)

    # Combine components.
    plot = area * curve

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plot = plot.opts(hv.opts.Overlay(title=title))

    # Add legend.
    plot = plot.opts(legend_position="top_left", legend_opts={"click_policy": "hide", "orientation": "horizontal"},
                     frame_height=300, frame_width=645, border_line_alpha=0.0, background_fill_alpha=0.0)

    return plot

    
def gen_cycle_d_mat(
    df: pd.DataFrame,
    plt_type: Optional[int] = 1
) -> Union[plt.Figure, None]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a time series of daily values using matplotlib.

    Parameters
    ----------
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
    height = 5.45 if cntx.code == c.platform_streamlit else 5.15
    fig, ax = plt.subplots(figsize=(9.95, height), dpi=cntx.dpi)
    plt.subplots_adjust(top=0.99, bottom=0.13, left=0.08, right=0.98, hspace=0.10, wspace=0.10)

    # Draw areas.
    ref_color = def_rcp.RCP(c.ref).color
    rcp_color = "darkgrey"
    if plt_type == 1:
        ax.plot(range(1, n + 1), df[c.stat_mean], color=ref_color, alpha=1.0)
        ax.fill_between(np.array(range(1, n + 1)), df[c.stat_mean], df[c.stat_max], color=rcp_color, alpha=1.0)
        ax.fill_between(np.array(range(1, n + 1)), df[c.stat_mean], df[c.stat_min], color=rcp_color, alpha=1.0)
    else:
        bar_width = 1.0
        plt.bar(range(1, n + 1), df[c.stat_max], width=bar_width, color=rcp_color)
        plt.bar(range(1, n + 1), df[c.stat_mean], width=bar_width, color=rcp_color)
        plt.bar(range(1, n + 1), df[c.stat_min], width=bar_width, color="white")
        ax.plot(range(1, n + 1), df[c.stat_mean], color=ref_color, alpha=1.0)
        y_lim_lower = min(df[c.stat_min])
        y_lim_upper = max(df[c.stat_max])
        plt.ylim([y_lim_lower, y_lim_upper])

    # Format.
    plt.xlim([1, n])
    plt.xticks(np.arange(1, n + 1, 30))
    plt.xlabel("Jour", fontsize=fs_axes)
    y_label = ("Δ" if cntx.delta.code == "True" else "") + cntx.varidx.label
    plt.ylabel(y_label, fontsize=fs_axes)
    plt.tick_params(axis="x", labelsize=fs_axes)
    plt.tick_params(axis="y", labelsize=fs_axes)

    # Title.
    title = str(plot_title()) + "\n" + str(plot_code())
    plt.title(title, loc="left", fontweight="bold")

    # Format.
    plt.legend(["Valeur moyenne", "Étendue des valeurs"], fontsize=fs_legend)

    # Close plot.
    plt.close(fig)
    
    return fig


def plot_title(
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get plot title.

    Returns
    -------
    str
        Plot title.
    --------------------------------------------------------------------------------------------------------------------
    """

    return cntx.varidx.title


def plot_code(
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get plot code.

    Returns
    -------
    str
        Plot code.
    --------------------------------------------------------------------------------------------------------------------
    """

    code = ""

    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_cycle]:
        code = cntx.varidx.code
        if cntx.rcp.code not in ["", c.rcpxx]:
            code += " - " + cntx.rcp.desc
        if cntx.view.code == c.view_cycle:
            code += " - " + cntx.hor.code
        if cntx.sim.code not in ["", c.simxx]:
            code += " - " + cntx.sim.rcm + "_" + cntx.sim.gcm
            if (cntx.rcp.code in ["", c.rcpxx]) and (cntx.sim.rcp is not None):
                code += " (" + cntx.sim.rcp.desc + ")"

    elif cntx.view.code == c.view_tbl:
        code = cntx.varidx.code + " - " + cntx.hor.code

    elif cntx.view.code == c.view_map:
        code = cntx.varidx.code + " - " + cntx.hor.code + " - " + cntx.rcp.desc
        if cntx.rcp.code != c.ref:
            code += " - " + cntx.stat.desc

    return ("Δ" if cntx.delta.code == "True" else "") + code


def gen_cluster_tbl(
    n_cluster: int
) -> pd.DataFrame:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate cluster table (based on time series).

    Parameters
    ----------
    n_cluster: int
        Number of clusters.

    Returns
    -------
    pd.DataFrame
    --------------------------------------------------------------------------------------------------------------------
    """

    # Column names.
    col_sim = "Simulation"
    col_rcp = "RCP"
    col_grp = "Groupe"

    # Calculate clusters.
    df = pd.DataFrame(stats.calc_clusters(n_cluster))

    # Subset columns and sort rows.
    df = df[[col_sim, col_rcp, col_grp]]
    df.sort_values(by=[col_grp, col_rcp], inplace=True)

    # Title.
    vars_str = str(cntx.varidxs.code_l).replace("[", "").replace("]", "").replace("'", "")
    title = "<b>Regroupement des simulations par similarité<br>=f(" + vars_str + ")</b>"

    # In Jupyter Notebook, a dataframe appears nicely.
    if cntx.code == c.platform_jupyter:
        tbl = df.set_index(df.columns[0])

    # In Streamlit, a table needs to be formatted.
    else:

        # Determine text colors.
        cmap = plt.cm.get_cmap("rainbow", n_cluster)
        text_color_l = []
        for i in range(n_cluster):
            text_color_l_i = []
            for j in range(len(df)):
                group = df[col_grp].values[j]
                text_color_l_i.append(colors.to_hex(cmap((group - 1) / (n_cluster - 1))))
            text_color_l.append(text_color_l_i)

        # Values.
        values = []
        for col_name in df.columns:
            values.append(df[col_name])

        # Table
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),
                        line_color="white",
                        fill_color=cntx.col_sb_fill,
                        align="right"),
            cells=dict(values=values,
                       font=dict(color=text_color_l),
                       line_color="white",
                       fill_color="white",
                       align="right"))
        ])
        fig.update_layout(
            font=dict(size=15),
            width=700,
            height=50 + 23 * len(df),
            margin=go.layout.Margin(l=0, r=0, b=0, t=50),
            title_text=title,
            title_x=0,
            title_font=dict(size=15)
        )
        tbl = fig

    return tbl


def gen_cluster_plot(
    n_cluster: int
) -> Union[any, plt.figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a cluster scatter plot (based on time series).

    Parameters
    ----------
    n_cluster: int
        Number of clusters.

    Returns
    -------
    Union[any, plt.figure] :
        Cluster scatter plot.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Calculate clusters.
    df = pd.DataFrame(stats.calc_clusters(n_cluster))

    # Extract variables.
    if cntx.varidxs.count == 1:
        var_1 = var_2 = cntx.varidxs.items[0]
    else:
        var_1 = cntx.varidxs.items[0]
        var_2 = cntx.varidxs.items[1]

    # Title.
    vars_str = str(cntx.varidxs.code_l).replace("[", "").replace("]", "").replace("'", "")
    title = "Regroupement des simulations par similarité\n=f(" + vars_str + ")"

    # Labels.
    x_label = var_1.desc + " (" + var_1.unit + ")"
    y_label = var_2.desc + " (" + var_2.unit + ")"

    # Color map.
    cmap = plt.cm.get_cmap("rainbow", n_cluster)

    # Generate plot.
    if cntx.lib.code == c.lib_mat:
        plot = gen_cluster_plot_mat(df, var_1, var_2, title, x_label, y_label, cmap)
    else:
        plot = gen_cluster_plot_hv(df, var_1, var_2, title, x_label, y_label, cmap)

    return plot


def gen_cluster_plot_hv(
    df: pd.DataFrame,
    var_1: vi.VarIdx,
    var_2: vi.VarIdx,
    title: str,
    x_label: str,
    y_label: str,
    cmap: Union[colors.Colormap, str]
) -> any:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a cluster scatter plot (based on time series) using hvplot.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe.
    var_1: vi.VarIdx
        First variable.
    var_2: vi.VarIdx
        Second variable.
    title: str
        Title.
    x_label: str
        X-label.
    y_label: str
        Y-label.
    cmap: Union[colors.Colormap, str]
        Color map.

    Returns
    -------
    any
        Cluster scatter plot.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Column names.
    col_sim = "Simulation"
    col_rcp = "RCP"
    col_grp = "Groupe"

    # Number of clusters.
    n_cluster = len(df[col_grp].unique())

    # Adjust precision (not working great).
    # df[var_1.code] = adjust_precision(list(df[var_1.code].values), n_dec_max=var_1.precision, output_type="float")
    # df[var_2.code] = adjust_precision(list(df[var_2.code].values), n_dec_max=var_2.precision, output_type="float")

    # Rename columns.
    df.rename(columns={var_1.code: var_1.desc, var_2.code: var_2.desc}, inplace=True)

    # Add point layers.
    plot = None
    for i in range(n_cluster):

        # Select the rows corresponding to the current cluster.
        df_i = df[df[col_grp] == i + 1]

        # Color.
        color = cmap(i / (n_cluster - 1))

        # Add point layer.
        # label=(col_grp + " " + str(i + 1))
        plot_i = df_i.hvplot.scatter(x=var_1.desc, y=var_2.desc, color=color,
                                     hover_cols=[col_sim, col_rcp, col_grp, var_1.desc, var_2.desc])
        plot = plot_i if plot is None else plot * plot_i

    # Title.
    plot = plot.opts(hv.opts.Overlay(title=title))

    # Adjust size and add legend.
    # legend_position="top_left", legend_opts={"click_policy": "hide", "orientation": "horizontal"}
    plot = plot.opts(frame_height=300, frame_width=645, border_line_alpha=0.0, background_fill_alpha=0.0,
                     xlabel=x_label, ylabel=y_label)

    return plot


def gen_cluster_plot_mat(
    df: pd.DataFrame,
    var_1: vi.VarIdx,
    var_2: vi.VarIdx,
    title: str,
    x_label: str,
    y_label: str,
    cmap: Union[colors.Colormap, str]
) -> plt.Figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Plot a cluster scatter plot (based on time series) using matplotlib.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe.
    var_1: vi.VarIdx
        First variable.
    var_2: vi.VarIdx
        Second variable.
    title: str
        Title.
    x_label: str
        X-label.
    y_label: str
        Y-label.
    cmap: Union[colors.Colormap, str]
        Color map.

    Returns
    -------
    plt.Figure
        Figure
    --------------------------------------------------------------------------------------------------------------------
    """

    # Column names.
    col_grp = "Groupe"

    # Number of clusters.
    n_cluster = len(df[col_grp].unique())

    # Font size.
    fs        = 9 if cntx.code == c.platform_streamlit else 10
    fs_title  = fs + 1
    # fs_labels = fs

    # Initialize figure and axes.
    if c.platform_streamlit in cntx.code:
        fig = plt.figure(figsize=(9, 4.4), dpi=cntx.dpi)
    else:
        fig = plt.figure(figsize=(10.6, 4.8), dpi=cntx.dpi)
        plt.subplots_adjust(top=0.98, bottom=0.10, left=0.08, right=0.92, hspace=0.0, wspace=0.0)
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:])

    # Format.
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Create scatter plot (matplotlib).
    leg_labels = []
    leg_lines = []
    for i in range(n_cluster):
        color = cmap(i / (n_cluster - 1))
        ax.scatter(x=df[df[col_grp] == i + 1][var_1.code], y=df[df[col_grp] == i + 1][var_2.code], color=color)
        leg_labels.append(col_grp + " " + str(i + 1))
        leg_lines.append(Line2D([0], [0], color=color, lw=2))
    plt.legend()

    # Title.
    plt.title(title, loc="left", fontweight="bold", fontsize=fs_title)

    # Legend.
    # ax.legend(leg_lines, leg_labels, loc="upper left", ncol=5, mode="expland", frameon=False,
    #           fontsize=fs_labels)

    plt.close(fig)

    return fig
