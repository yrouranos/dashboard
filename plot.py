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
import config as cf
import context_def
import holoviews as hv
import hvplot.pandas
import lib_def
import math
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import panel as pn
import plotly.graph_objects as go
import plotly.io as pio
import rcp_def
import simplejson
import stat_def
import utils
import varidx_def as vi
import xarray as xr
from descartes import PolygonPatch
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import Union, List

import view_def

alt.renderers.enable("default")
pn.extension("vega")
hv.extension("bokeh", logo=False)
pio.renderers.default = "iframe"


def gen_ts(
    cntx: context_def.Context
) -> Union[alt.Chart, plt.figure]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    
    Returns
    -------
    Union[alt.Chart, plt.figure] :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """
       
    # Load data.
    df = utils.load_data(cntx)

    # Calculate deltas.
    if cntx.delta:
        for col in df.columns[2:]:
            if col != rcp_def.rcp_ref:
                df[col] = df[col] - df[rcp_def.rcp_ref].mean()

    # Extract minimum and maximum x-values (round to lower and upper decades).
    x_min = math.floor(min(df["year"]) / 10) * 10
    x_max = math.ceil(max(df["year"]) / 10) * 10
    
    # Extract minimum and maximum y-values.
    first_col_index = 3 if cntx.delta else 2
    y_min = df.iloc[:, first_col_index:].min().min()
    y_max = df.iloc[:, first_col_index:].max().max()
    for rcp in cntx.rcps.items:
        if rcp.get_code() == rcp_def.rcp_ref:
            col_min = col_max = rcp_def.rcp_ref
        else:
            col_min = rcp.get_code() + "_min"
            col_max = rcp.get_code() + "_max"
        if col_min in df.columns:
            y_min = min(y_min, df[col_min].min())
        if col_max in df.columns:
            y_max = max(y_max, df[col_max].max())

    # Plot components.
    x_label = "Année"
    y_label = ("Δ" if cntx.delta else "") + cntx.varidx.get_label()
    
    if cntx.lib.get_code() == lib_def.mode_mat:
        ts = gen_ts_mat(cntx, df, x_label, y_label, [x_min, x_max], [y_min, y_max])
    elif cntx.lib.get_code() == lib_def.mode_hv:
        ts = gen_ts_hv(cntx, df, x_label, y_label)
    else:
        ts = gen_ts_alt(cntx, df, x_label, y_label, [y_min, y_max])
        
    return ts


def gen_ts_alt(
    cntx: context_def.Context,
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
    y_range: List[float]
) -> alt.Chart:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series using altair.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    x_label : str
        X-label.
    y_label : str
        Y-label.
    y_range : List[str]
        Range of y_values to display [{y_min}, {y_max}].
        
    Returns
    -------
    alt.Chart :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Plot components.
    x_axis = alt.Axis(title=x_label, format="d")
    y_axis = alt.Axis(title=y_label, format="d")
    y_scale = alt.Scale(domain=y_range)
    col_legend = alt.Legend(title="", orient="top-left", direction="horizontal", symbolType="stroke")
    col_scale = alt.Scale(range=cntx.rcps.get_color_l(), domain=cntx.rcps.get_desc_l())
    
    # Add layers.
    plot = None
    for item in ["area", "curve"]:
        for rcp in cntx.rcps.items:
            
            if rcp.get_code() == rcp_def.rcp_ref:
                df_rcp = df[["year", rcp.get_code()]].copy()
                df_rcp.insert(len(df_rcp.columns), "rcp", rcp.get_desc())
                df_rcp.rename(columns={rcp_def.rcp_ref: "mean"}, inplace=True)
                df_rcp.insert(len(df_rcp.columns), "minimum", df_rcp["mean"])
                df_rcp.insert(len(df_rcp.columns), "maximum", df_rcp["mean"])
                tooltip = ["year", "rcp", "mean"]
            else:
                df_rcp = df[["year",
                             str(rcp.get_code() + "_min"),
                             str(rcp.get_code() + "_moy"),
                             str(rcp.get_code() + "_max")]].copy()
                df_rcp.insert(len(df_rcp.columns), "rcp", rcp.get_desc())
                df_rcp.rename(columns={str(rcp.get_code() + "_min"): "minimum",
                                       str(rcp.get_code() + "_moy"): "mean",
                                       str(rcp.get_code() + "_max"): "maximum"}, inplace=True)
                tooltip = ["year", "rcp", "minimum", "mean", "maximum"]
            
            # Draw area.
            area = None
            curve = None
            if item == "area":
                area = alt.Chart(df_rcp).mark_area(opacity=0.3, text=rcp.get_desc()).encode(
                    x=alt.X("year", axis=x_axis),
                    y=alt.Y("minimum", axis=y_axis, scale=y_scale),
                    y2="maximum",
                    color=alt.Color("rcp", scale=col_scale)
                )
            
            # Draw curve.
            else:
                curve = alt.Chart(df_rcp).mark_line(opacity=1.0, text=rcp.get_desc()).encode(
                    x=alt.X("year", axis=x_axis),
                    y=alt.Y("mean", axis=y_axis, scale=y_scale),
                    color=alt.Color("rcp", scale=col_scale, legend=col_legend),
                    tooltip=tooltip
                ).interactive()

            # Combine parts.
            if plot is None:
                if item == "area":
                    plot = area
                else:
                    plot = curve
            else:
                if item == "area":
                    plot = plot + area
                else:
                    plot = plot + curve

    return plot.configure_axis(grid=False).properties(height=365, width=705)


def gen_ts_hv(
    cntx: context_def.Context,
    df: pd.DataFrame,
    x_label: str,
    y_label: str
) -> hvplot:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series using hvplot.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    df : pd.DataFrame
        Dataframe.
    x_label : str
        X-label.
    y_label : str
        Y-label.
        
    Returns
    -------
    str :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Loop through RCPs.
    plot = None
    for item in ["area", "curve"]:
        for rcp in cntx.rcps.items:

            if (item == "area") and (rcp.get_code() == rcp_def.rcp_ref):
                continue
                
            # Draw area.
            area = None
            curve = None
            if item == "area":
                area = df.hvplot.area(x="year",
                                      y=str(rcp.get_code() + "_min"),
                                      y2=str(rcp.get_code() + "_max"),
                                      color=rcp.get_color(), alpha=0.3, line_alpha=0,
                                      xlabel=x_label, ylabel=y_label)
            
            # Draw curve.
            else:
                y = rcp_def.rcp_ref if rcp.get_code() == rcp_def.rcp_ref else str(rcp.get_code() + "_moy")
                curve = df.hvplot.line(x="year",
                                       y=y,
                                       color=rcp.get_color(), alpha=0.7, label=rcp.get_desc())

            # Combine parts.
            if plot is None:
                if item == "area":
                    plot = area
                else:
                    plot = curve
            else:
                if item == "area":
                    plot = plot * area
                else:
                    plot = plot * curve 
            
    # Add legend.
    plot = plot.opts(legend_position="top_left", legend_opts={"click_policy": "hide", "orientation": "horizontal"},
                     frame_height=300, frame_width=645, border_line_alpha=0.0, background_fill_alpha=0.0)
    
    return plot


def gen_ts_mat(
    cntx: context_def.Context,
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
    x_range: List[float],
    y_range: List[float]
) -> plt.figure:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series using matplotlib.
    
    Parameters
    ----------
    cntx : context_def.Context
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
        
    Returns
    -------
    plt.figure :
        Plot of time series.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Initialize plot.
    fig = plt.figure(figsize=(9, 4.45), dpi=cf.dpi)
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticks(range(x_range[0], x_range[1] + 10, 10), minor=False)
    ax.set_xticks(range(x_range[0], x_range[1] + 5, 5), minor=True)
    plt.xlim(x_range[0], x_range[1])
    plt.ylim(y_range[0], y_range[1])

    # Loop through RCPs.
    leg_labels = []
    leg_lines = []
    for rcp in cntx.rcps.items:

        # Extract columns.
        data_year = df.year
        data_rcp = []
        if (rcp.get_code() == rcp_def.rcp_ref) and (rcp_def.rcp_ref in df.columns):
            data_rcp = df[rcp_def.rcp_ref]
        elif (rcp.get_code() != rcp_def.rcp_ref) and (str(rcp.get_code() + "_moy") in df.columns):
            data_rcp = [df[rcp.get_code() + "_min"], df[rcp.get_code() + "_moy"], df[rcp.get_code() + "_max"]]
                          
        # Skip if no data is available for this RCP.
        if len(data_rcp) == 0:
            continue

        # Add curves and areas.
        color = rcp.get_color()
        if rcp.get_code() == rcp_def.rcp_ref:
            ax.plot(data_year, data_rcp, color=color, alpha=1.0)
        else:
            ax.plot(data_year, data_rcp[1], color=color, alpha=1.0)
            ax.fill_between(np.array(data_year), data_rcp[0], data_rcp[2], color=color, alpha=0.25)
        
        # Collect legend label and line.
        leg_labels.append(rcp.get_desc())    
        leg_lines.append(Line2D([0], [0], color=color, lw=2))

    # Build legend.
    ax.legend(leg_lines, leg_labels, loc="upper left", ncol=len(leg_labels), mode="expland", frameon=False)
    
    plt.close(fig)
    
    return fig


def gen_tbl(
    cntx: context_def.Context
) -> Union[pd.DataFrame, go.Figure]:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a table.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.

    Returns
    -------
    Union[pd.DataFrame, go.Figure] :
        Dataframe or figure.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    df = utils.load_data(cntx)

    # List of statistics (in a column).
    stat_l, stat_desc_l = [], []
    for code in list(stat_def.code_desc.keys()):
        if code in [stat_def.mode_min, stat_def.mode_max, stat_def.mode_mean]:
            stat_l.append([code, -1])
        elif code == "q" + cntx.project.get_quantiles_as_str()[0]:
            stat_l.append(["quantile", cntx.project.get_quantiles()[0]])
        elif code == "q" + cntx.project.get_quantiles_as_str()[1]:
            stat_l.append(["quantile", cntx.project.get_quantiles()[1]])
        else:
            stat_l.append(["quantile", 0.5])
        stat_desc_l.append(stat_def.code_desc[code])

    # Initialize resulting dataframe.
    df_res = pd.DataFrame()
    df_res["Statistique"] = stat_desc_l

    # Loop through RCPs.
    columns = []
    for rcp in cntx.rcps.items:

        if rcp.get_code() == rcp_def.rcp_ref:
            continue

        # Extract delta.
        delta = 0.0
        if cntx.delta:
            delta = float(df[df["rcp"] == rcp_def.rcp_ref]["val"])

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

    if cntx.platform == "jupyter":
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
                        fill_color=cf.col_sb_fill,
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
    cntx: context_def.Context
) -> str:
    
    """
    --------------------------------------------------------------------------------------------------------------------
    Get the reference value.

    Parameters
    ----------
    cntx : context_def.Context
        Context.
        
    Returns
    -------
    str
        Reference value and unit.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    cntx_tbl = cntx.copy()
    cntx_tbl.view = view_def.View(view_def.mode_tbl)
    df = utils.load_data(cntx_tbl)
    
    # Extract value.
    val = df[df["rcp"] == rcp_def.rcp_ref]["val"][0]
    if cntx.varidx.get_precision == 0:
        val = int(val)
    val = str(val)
    unit = cntx.varidx.get_unit()
    if unit != "°C":
        val += " "
    
    return val + unit


def gen_map(
    cntx: context_def.Context
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate a plot of time series.
    
    Parameters
    ----------
    cntx : context_def.Context
        Context.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Load data.
    df = utils.load_data(cntx)

    # Hardcoded parameters.
    # Number of clusters (for discrete color scale).
    if cf.opt_map_discrete:
        n_cluster = 10
    else:
        n_cluster = 256
    # Maximum number of decimal places for colorbar ticks.
    n_dec_max = 4
    # Font size.
    fs_title      = 5
    fs_labels     = 5
    fs_ticks      = 5
    fs_ticks_cbar = 5
    if cntx.delta:
        fs_ticks_cbar = fs_ticks_cbar - 1

    # Title and label.
    title = ""
    label = ("Δ" if cntx.delta else "") + cntx.varidx.get_label()

    # Find minimum and maximum values (consider all relevant CSV files).
    z_min, z_max = utils.get_min_max(cntx)
    
    # Determine color scale index.
    is_wind_var = cntx.varidx.get_code() in [vi.var_uas, vi.var_vas, vi.var_sfcwindmax]
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
        [vi.var_tas, vi.var_tasmin, vi.var_tasmax, vi.idx_etr, vi.idx_tgg,
         vi.idx_tng, vi.idx_tnx, vi.idx_txx, vi.idx_txg]:
        cmap_name = cf.opt_map_col_temp_var[cmap_idx]
    elif cntx.varidx.get_code() in \
        [vi.idx_tx_days_above, vi.idx_heat_wave_max_length, vi.idx_heat_wave_total_length,
         vi.idx_hot_spell_frequency, vi.idx_hot_spell_max_length, vi.idx_tropical_nights,
         vi.idx_tx90p, vi.idx_wsdi]:
        cmap_name = cf.opt_map_col_temp_idx_1[cmap_idx]
    elif cntx.varidx.get_code() in [vi.idx_tn_days_below, vi.idx_tng_months_below]:
        cmap_name = cf.opt_map_col_temp_idx_2[cmap_idx]

    # Precipitation-related.
    elif cntx.varidx.get_code() in \
        [vi.var_pr, vi.idx_prcptot, vi.idx_rx1day, vi.idx_rx5day, vi.idx_sdii,
         vi.idx_rain_season_prcptot]:
        cmap_name = cf.opt_map_col_prec_var[cmap_idx]
    elif cntx.varidx.get_code() in \
        [vi.idx_cwd, vi.idx_r10mm, vi.idx_r20mm, vi.idx_wet_days, vi.idx_rain_season_length,
         vi.idx_rnnmm]:
        cmap_name = cf.opt_map_col_prec_idx_1[cmap_idx]
    elif cntx.varidx.get_code() in \
        [vi.idx_cdd, vi.idx_dry_days, vi.idx_drought_code,
         vi.idx_dry_spell_total_length]:
        cmap_name = cf.opt_map_col_prec_idx_2[cmap_idx]
    elif cntx.varidx.get_code() in [vi.idx_rain_season_start, vi.idx_rain_season_end]:
        cmap_name = cf.opt_map_col_prec_idx_3[cmap_idx]

    # Wind-related.
    elif cntx.varidx.get_code() in [vi.var_uas, vi.var_vas, vi.var_sfcwindmax]:
        cmap_name = cf.opt_map_col_wind_var[cmap_idx]
    elif cntx.varidx.get_code() in [vi.idx_wg_days_above, vi.idx_wx_days_above]:
        cmap_name = cf.opt_map_col_wind_idx_1[cmap_idx]

    # Default values.
    else:
        cmap_name = cf.opt_map_col_default[cmap_idx]

    # Adjust minimum and maximum values so that zero is attributed the intermediate color in a scale or
    # use only the positive or negative side of the color scale if the other part is not required.
    if (z_min < 0) and (z_max > 0):
        vmax_abs = max(abs(z_min), abs(z_max))
        vmin = -vmax_abs
        vmax = vmax_abs
        n_cluster = n_cluster * 2
    else:
        vmin = z_min
        vmax = z_max

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

    hex_l = None
    if "Pinks" in cmap_name:
        hex_l = [hex_wh, hex_pi]
    elif "PiPu" in cmap_name:
        hex_l = [hex_pi, hex_wh, hex_pu]
    elif "Browns" in cmap_name:
        hex_l = [hex_wh, hex_br]
    elif "YlBr" in cmap_name:
        hex_l = [hex_yl, hex_br]
    elif "BrYlGr" in cmap_name:
        hex_l = [hex_br, hex_yl, hex_gr]
    elif "YlGr" in cmap_name:
        hex_l = [hex_yl, hex_gr]
    elif "BrWhGr" in cmap_name:
        hex_l = [hex_br, hex_wh, hex_gr]
    elif "TuYlSa" in cmap_name:
        hex_l = [hex_tu, hex_yl, hex_sa]
    elif "YlTu" in cmap_name:
        hex_l = [hex_yl, hex_tu]
    elif "YlSa" in cmap_name:
        hex_l = [hex_yl, hex_sa]
    elif "LBuWhLBr" in cmap_name:
        hex_l = [hex_lbu, hex_wh, hex_lbr]
    elif "LBlues" in cmap_name:
        hex_l = [hex_wh, hex_lbu]
    elif "BuYlRd" in cmap_name:
        hex_l = [hex_bu, hex_yl, hex_rd]
    elif "LBrowns" in cmap_name:
        hex_l = [hex_wh, hex_lbr]
    elif "LBuYlLBr" in cmap_name:
        hex_l = [hex_lbu, hex_yl, hex_lbr]
    elif "YlLBu" in cmap_name:
        hex_l = [hex_yl, hex_lbu]
    elif "YlLBr" in cmap_name:
        hex_l = [hex_yl, hex_lbr]
    elif "YlBu" in cmap_name:
        hex_l = [hex_yl, hex_bu]
    elif "Turquoises" in cmap_name:
        hex_l = [hex_wh, hex_tu]
    elif "PuYlOr" in cmap_name:
        hex_l = [hex_pu, hex_yl, hex_or]
    elif "YlOrRd" in cmap_name:
        hex_l = [hex_yl, hex_or, hex_rd]
    elif "YlOr" in cmap_name:
        hex_l = [hex_yl, hex_or]
    elif "YlPu" in cmap_name:
        hex_l = [hex_yl, hex_pu]
    elif "GyYlRd" in cmap_name:
        hex_l = [hex_gy, hex_yl, hex_rd]
    elif "YlGy" in cmap_name:
        hex_l = [hex_yl, hex_gy]
    elif "YlRd" in cmap_name:
        hex_l = [hex_yl, hex_rd]
    elif "GyWhRd" in cmap_name:
        hex_l = [hex_gy, hex_wh, hex_rd]

    # Build custom map.
    if hex_l is not None:

        # List of positions.
        if len(hex_l) == 2:
            pos_l = [0.0, 1.0]
        else:
            pos_l = [0.0, 0.5, 1.0]

        # Custom map.
        if "_r" not in cmap_name:
            cmap = build_custom_cmap(hex_l, n_cluster, pos_l)
        else:
            hex_l.reverse()
            cmap = build_custom_cmap(hex_l, n_cluster, pos_l)

    # Build Matplotlib map.
    else:
        cmap = plt.cm.get_cmap(cmap_name, n_cluster)

    # Calculate ticks.
    ticks = None
    str_ticks = None
    if cf.opt_map_discrete:
        ticks = []
        for i in range(n_cluster + 1):
            tick = i / float(n_cluster) * (vmax - vmin) + vmin
            ticks.append(tick)

        # Adjust tick precision.
        str_ticks = adjust_precision(ticks, n_dec_max)

    # Adjust minimum and maximum values.
    if ticks is None:
        vmin_adj = vmin
        vmax_adj = vmax
    else:
        vmin_adj = ticks[0]
        vmax_adj = ticks[n_cluster]

    # Create figure.
    fig = plt.figure(figsize=(4.5, 4), dpi=cf.dpi)
    ax = fig.add_subplot(1, 1, 1, aspect="equal")

    # Convert to DataArray.
    df = pd.DataFrame(df, columns=["longitude", "latitude", cntx.varidx.get_code()])
    df = df.sort_values(by=["latitude", "longitude"])
    lat = list(set(df["latitude"]))
    lat.sort()
    lon = list(set(df["longitude"]))
    lon.sort()
    arr = np.reshape(list(df[cntx.varidx.get_code()]), (len(lat), len(lon)))
    da = xr.DataArray(data=arr, dims=["latitude", "longitude"], coords=[("latitude", lat), ("longitude", lon)])

    # Create mesh.
    cbar_ax = make_axes_locatable(ax).append_axes("right", size="5%", pad=0.05)
    da.plot.pcolormesh(cbar_ax=cbar_ax, add_colorbar=True, add_labels=True,
                       ax=ax, cbar_kwargs=dict(orientation='vertical', pad=0.05, label=label, ticks=ticks),
                       cmap=cmap, vmin=vmin_adj, vmax=vmax_adj)

    # Format.
    ax.set_title(title, fontsize=fs_title)
    ax.set_xlabel("Longitude (º)", fontsize=fs_labels)
    ax.set_ylabel("Latitude (º)", fontsize=fs_labels)
    ax.tick_params(axis="x", labelsize=fs_ticks, length=0, rotation=90)
    ax.tick_params(axis="y", labelsize=fs_ticks, length=0)
    cbar_ax.set_ylabel(label, fontsize=fs_labels)
    cbar_ax.tick_params(labelsize=fs_ticks_cbar, length=0)
    if cf.opt_map_discrete:
        cbar_ax.set_yticklabels(str_ticks)

    # Draw region boundary.
    draw_region_boundary(cntx, ax)

    plt.close(fig)
    
    return fig


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


def build_custom_cmap(
    hex_l: [str],
    n_cluster: int,
    pos_l: [float] = None
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Create a color map that can be used in heat map figures.
    
    If pos_l is not provided, color map graduates linearly between each color in hex_l.
    If pos_l is provided, each color in hex_l is mapped to the respective location in pos_l.

    Parameters
    ----------
    hex_l: [str]
        List of hex code strings.
    n_cluster: int
        Number of clusters.
    pos_l: [float]
        List of positions (float between 0 and 1), same length as hex_l. Must start with 0 and end with 1.

    Returns
    -------
        Color map.
    --------------------------------------------------------------------------------------------------------------------
    """

    rgb_l = [rgb_to_dec(hex_to_rgb(i)) for i in hex_l]
    if pos_l:
        pass
    else:
        pos_l = list(np.linspace(0, 1, len(rgb_l)))

    cdict = dict()
    for num, col in enumerate(["red", "green", "blue"]):
        col_l = [[pos_l[i], rgb_l[i][num], rgb_l[i][num]] for i in range(len(pos_l))]
        cdict[col] = col_l
    cmp = colors.LinearSegmentedColormap("custom_cmp", segmentdata=cdict, N=n_cluster)

    return cmp


def draw_region_boundary(
    cntx: context_def.Context,
    ax: plt.axes
) -> plt.axes:

    """
    --------------------------------------------------------------------------------------------------------------------
    Draw region boundary.

    Parameters
    ----------
    cntx: context_def.Context
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

    # Read geojson file.
    with open(utils.get_p_bounds(cntx)) as f:
        pydata = simplejson.load(f)

    # Draw feature.
    ax_new = ax
    coordinates = pydata["features"][0]["geometry"]["coordinates"][0]
    vertices = coordinates[0]
    if len(vertices) == 2:
        coordinates = pydata["features"][0]["geometry"]["coordinates"]
        vertices = coordinates[0]
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
