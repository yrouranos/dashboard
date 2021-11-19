import altair as alt
import hvplot.pandas
import logging
import math
import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import panel as pn
import utils
import warnings
from matplotlib.lines import Line2D
from typing import Union, List

view_list = ["Série temporelle", "Tableau", "Carte"]
plot_libs = ["altair", "hvplot", "matplotlib"]
cols      = {"ref": "black", "rcp26": "blue", "rcp45": "green", "rcp85": "red"}

alt.renderers.enable("default")
pn.extension("vega")


def get_col_list(rcp_list: List[str]) -> List[str]:
    
    """
    Extract color names associated with each one of the items in a RCP list.
    
    Parameters
    ----------
    rcp_list: List[str]
        List of RCPs.
    
    """
    
    col_list = []
    for rcp in rcp_list:
        col_list.append(cols[rcp])
        
    return col_list


def gen_ts(var_or_idx: str, lib: str = "altair") -> Union[alt.Chart, plt.figure]:

    """
    Generate a plot of time series.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    lib : str
        Plotting library = {"altair", "matplotlib", "hvplot"}
        
    Returns
    -------
    Union[alt.Chart, plt.figure] :
        Plot of time series.
    """
       
    # Load data.
    df = utils.load_data(var_or_idx, "ts")

    # Extract RCPs.
    rcp_list = utils.get_rcp_list(var_or_idx, "ts")
    
    # Extract minimum and maximum x-values (round to lower and upper decades).
    x_min = math.floor(min(df["year"]) / 10) * 10
    x_max = math.ceil(max(df["year"]) / 10) * 10
    
    # Extract minimum and maximum y-values.
    y_min = df[utils.ref].min()
    y_max = df[utils.ref].max()
    for rcp in rcp_list:
        if rcp == utils.ref:
            y_min = min(y_min, df[utils.ref].min())
            y_max = max(y_max, df[utils.ref].max())
        else:
            y_min = min(y_min, df[rcp + "_min"].min())
            y_max = max(y_max, df[rcp + "_max"].max())
    
    # Plot components.
    title = utils.get_var_or_idx_name(var_or_idx)
    x_label = "Année"
    y_label = utils.get_var_or_idx_desc(var_or_idx)
    
    if lib == "matplotlib":
        ts = gen_ts_mat(df, var_or_idx, rcp_list, title, x_label, y_label, [x_min, x_max], [y_min, y_max])
    elif lib == "hvplot":
        ts = gen_ts_hv(df, var_or_idx, rcp_list, title, x_label, y_label, [y_min, y_max])
    else:
        ts = gen_ts_alt(df, var_or_idx, rcp_list, title, x_label, y_label, [y_min, y_max])
        
    return ts


def gen_ts_alt(df: pd.DataFrame, var_or_idx: str, rcp_list: List[str], title: str, x_label: str, y_label: str,
               y_range: List[float]) -> alt.Chart:

    """
    Generate a plot of time series using altair.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe.
    var_or_idx : str
        Climate variable or index.
    rcp_list: List[str]
        List of RCPs.
    title : str
        Plot title.
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
    """
    
    # Plot components.
    x_axis = alt.Axis(title=x_label, format="d")
    y_axis = alt.Axis(title=y_label, format="d")
    y_scale = scale=alt.Scale(domain=y_range)
    col_scale = alt.Scale(range=get_col_list(rcp_list))
    # col_legend = alt.Legend(title="", direction="horizontal", orient="top", symbolType="stroke")
    col_legend = alt.Legend(title="", orient="top-left", direction="horizontal", symbolType="stroke")
    
    # Add layers.
    plot = None
    for item in ["area", "curve"]:
        for rcp in rcp_list:

            if (item == "area") and (rcp == utils.ref):
                continue
            
            if rcp == utils.ref:
                df_rcp = df[["year", utils.ref]].copy()
                df_rcp.insert(len(df_rcp.columns), "rcp", utils.get_rcp_desc(rcp))
                df_rcp.rename(columns={utils.ref: "mean"}, inplace=True)
                df_rcp.insert(len(df_rcp.columns), "minimum", df_rcp["mean"])
                df_rcp.insert(len(df_rcp.columns), "maximum", df_rcp["mean"])
                tooltip = ["year", "rcp", "mean"]
            else:
                df_rcp = df[["year", str(rcp + "_min"), str(rcp + "_moy"), str(rcp + "_max")]].copy()
                df_rcp.insert(len(df_rcp.columns), "rcp", utils.get_rcp_desc(rcp))
                df_rcp.rename(columns={str(rcp + "_min"): "minimum",
                                       str(rcp + "_moy"): "mean",
                                       str(rcp + "_max"): "maximum"}, inplace=True)
                tooltip = ["year", "rcp", "minimum", "mean", "maximum"]

            # Draw area.
            area = None
            curve = None
            if item == "area":
                area = alt.Chart(df_rcp).mark_area(opacity=0.3, text=utils.get_rcp_desc(rcp)).encode(
                    x=alt.X("year", axis=x_axis),
                    y=alt.Y("minimum", axis=y_axis, scale=y_scale),
                    y2="maximum",
                    color=alt.Color("rcp", scale=col_scale)
                )
            
            # Draw curve.
            else:
                curve = alt.Chart(df_rcp).mark_line(opacity=1.0, text=utils.get_rcp_desc(rcp)).encode(
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


def gen_ts_hv(df: pd.DataFrame, var_or_idx: str, rcp_list: List[str], title: str, x_label: str, y_label: str,
               y_range: List[float]) -> hvplot:

    """
    Generate a plot of time series using hvplot.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
        
    Returns
    -------
    str :
        Plot of time series.
    """
    
    # Loop through RCPs.
    plot = None
    for item in ["area", "curve"]:
        for rcp in rcp_list:

            if (item == "area") and (rcp == utils.ref):
                continue
                
            # Draw area.
            area = None
            curve = None
            if item == "area":
                area = df.hvplot.area(x="year", y=str(rcp + "_min"), y2=str(rcp + "_max"),
                                      color=cols[rcp], alpha=0.3, line_alpha=0,
                                      xlabel=x_label, ylabel=y_label)
            
            # Draw curve.
            else:
                curve = df.hvplot.line(x="year", y=utils.ref if rcp == utils.ref else str(rcp + "_moy"),
                                       color=cols[rcp], alpha=0.7, label=utils.get_rcp_desc(rcp))

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
                     frame_height=300, frame_width= 645, border_line_alpha=0.0, background_fill_alpha=0.0)
    
    return plot


def gen_ts_mat(df: pd.DataFrame, var_or_idx: str, rcp_list: List[str], title: str, x_label: str, y_label: str,
               x_range: List[float], y_range: List[float]) -> plt.figure:

    """
    Generate a plot of time series using matplotlib.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe.
    var_or_idx : str
        Climate variable or index.
    rcp_list: List[str]
        List of RCPs.
    title : str
        Plot title.
    x_label : str
        X-label.
    y_label : str
        Y-label.
    x_range : List[str]
        Range of x_values to display [{x_min}, {x_max}].
    y_range : List[str]
        Range of y_values to display [{y_min}, {y_max}].
        
    Returns
    -------
    plt.figure :
        Plot of time series.
    """
    
    # Initialize plot.
    fs = 9
    fig = plt.figure(figsize=(9, 4.45))
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
    for rcp in rcp_list:

        # Extract columns.
        data_year = df.year
        data_rcp = []
        if (rcp == utils.ref) and (utils.ref in df.columns):
            data_rcp = df[utils.ref]
        elif (rcp != utils.ref) and (str(rcp + "_moy") in df.columns):
            data_rcp = [df[rcp + "_min"], df[rcp + "_moy"], df[rcp + "_max"]]
                          
        # Skip if no data is available for this RCP.
        if len(data_rcp) == 0:
            continue

        # Add curves and areas.
        color = cols[rcp]
        if rcp == utils.ref:
            ax.plot(data_year, data_rcp, color=color, alpha=1.0)
        else:
            ax.plot(data_year, data_rcp[1], color=color, alpha=1.0)
            ax.fill_between(np.array(data_year), data_rcp[0], data_rcp[2], color=color, alpha=0.25)
        
        # Collect legend label and line.
        if rcp == utils.ref:
            leg_labels.append("Référence")
        else:
            leg_labels.append(utils.get_rcp_desc(rcp))    
        leg_lines.append(Line2D([0], [0], color=color, lw=2))

    # Build legend.
    ax.legend(leg_lines, leg_labels, loc="upper left", ncol=len(leg_labels), mode="expland", frameon=False)
    
    plt.close(fig)
    
    return fig


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
    df = utils.load_data(var_or_idx, "tbl")
    df = df.drop(df.columns[0:3], axis=1)
    
    return df