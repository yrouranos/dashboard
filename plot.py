import altair as alt
import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import utils
from matplotlib.lines import Line2D
from typing import Union

view_list = ["Série temporelle", "Tableau", "Carte"]
plot_libs = ["altair", "matplotlib"]
cols      = {"ref": "black", "rcp26": "blue", "rcp45": "green", "rcp85": "red"}

alt.renderers.enable("default")


def gen_ts(var_or_idx: str, lib: str = "altair") -> Union[alt.Chart, plt.figure]:

    """
    Generate a plot of time series.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
    lib : str
        Plotting library = {"altair", "matplotlib"}
        
    Returns
    -------
    Union[alt.Chart, plt.figure] :
        Plot of time series.
    """
        
    if lib == "matplotlib":
        ts = gen_ts_mat(var_or_idx)
    else:
        ts = gen_ts_alt(var_or_idx)
    
    return ts
        
        
def gen_ts_alt(var_or_idx: str) -> alt.Chart:

    """
    Generate a plot of time series using altair.
    
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
    df = utils.load_data(var_or_idx, "ts")

    # Extract RCPs.
    rcp_list = utils.get_rcp_list(var_or_idx, "ts")
    
    # Extract list of colors.
    col_list = []
    for rcp in rcp_list:
        col_list.append(cols[rcp])
        
    # Extract minimum and maximum.
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
    x_axis = alt.Axis(title="Année", format="d")
    y_axis = alt.Axis(title=utils.get_var_or_idx_desc(var_or_idx), format="d")
    y_scale = scale=alt.Scale(domain=[y_min, y_max])
    col_scale = alt.Scale(range=col_list)
    col_legend = alt.Legend(title="Scenarios")
    
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

    return plot.configure_axis(grid=False).properties(width=700, title=utils.get_var_or_idx_name(var_or_idx))


def gen_ts_mat(var_or_idx: str) -> plt.figure:

    """
    Generate a plot of time series using matplotlib.
    
    Parameters
    ----------
    var_or_idx : str
        Climate variable or index.
        
    Returns
    -------
    plt.figure :
        Plot of time series.
    """
        
    # Load data.
    df = utils.load_data(var_or_idx, "ts")

    # Extract RCPs.
    rcp_list = utils.get_rcp_list(var_or_idx, "ts")
    
    # Extract minimum and maximum.
    y_min = df[utils.ref].min()
    y_max = df[utils.ref].max()
    for rcp in rcp_list:
        if rcp == utils.ref:
            y_min = min(y_min, df[utils.ref].min())
            y_max = max(y_max, df[utils.ref].max())
        else:
            y_min = min(y_min, df[rcp + "_min"].min())
            y_max = max(y_max, df[rcp + "_max"].max())
        
    # Extract data from CSV.
    data_year = df.year
    data_ref = []
    if utils.ref in df.columns:
        data_ref = df[utils.ref]
    data_rcp26 = []
    if str(utils.rcp26 + "_moy") in df.columns:
        data_rcp26 = [df.rcp26_min, df.rcp26_moy, df.rcp26_max]
    data_rcp45 = []
    if str(utils.rcp45 + "_moy") in df.columns:
        data_rcp45 = [df.rcp45_min, df.rcp45_moy, df.rcp45_max]
    data_rcp85 = []
    if str(utils.rcp85 + "_moy") in df.columns:
        data_rcp85 = [df.rcp85_min, df.rcp85_moy, df.rcp85_max]

    # Fonts.
    fs_sup_title = 9
    title = utils.get_var_or_idx_name(var_or_idx)
    ylabel = utils.get_var_or_idx_desc(var_or_idx)

    # Initialize plot.
    fig = plt.figure(constrained_layout=True, figsize=(9, 5))
    specs = gridspec.GridSpec(ncols=1, nrows=1, figure=fig)
    ax = fig.add_subplot(specs[:])
    ax.set_title(title, fontsize=fs_sup_title)
    ax.set_xlabel("Année")
    ax.secondary_yaxis("right")
    ax.get_yaxis().tick_right()
    ax.axes.get_yaxis().set_visible(False)
    secax = ax.secondary_yaxis("right")
    secax.set_ylabel(ylabel)
    plt.subplots_adjust(top=0.925, bottom=0.10, left=0.03, right=0.90, hspace=0.30, wspace=0.416)

    # Loop through RCPs.
    for rcp in rcp_list:

        # Skip if no simulation is available for this RCP.
        if ((rcp == utils.ref) and (len(data_ref) == 0)) or \
           ((rcp == utils.rcp26) and (len(data_rcp26) == 0)) or \
           ((rcp == utils.rcp45) and (len(data_rcp45) == 0)) or \
           ((rcp == utils.rcp85) and (len(data_rcp85) == 0)):
            continue

        # Color.
        color = cols[rcp]

        # Add data.
        if rcp == utils.ref:
            ax.plot(data_year, data_ref, color=color, alpha=1.0)
        else:
            if rcp == utils.rcp26:
                data_mean = data_rcp26[1]
                data_min  = data_rcp26[0]
                data_max  = data_rcp26[2]
            elif rcp == utils.rcp45:
                data_mean = data_rcp45[1]
                data_min  = data_rcp45[0]
                data_max  = data_rcp45[2]
            elif rcp == utils.rcp85:
                data_mean = data_rcp85[1]
                data_min  = data_rcp85[0]
                data_max  = data_rcp85[2]
            ax.plot(data_year, data_mean, color=color, alpha=1.0)
            ax.fill_between(np.array(data_year), data_min, data_max, color=color, alpha=0.25)

    # Finalize plot.
    legend_l = ["Référence"]
    if utils.rcp26 in rcp_list:
        legend_l.append("RCP 2.6")
    if utils.rcp45 in rcp_list:
        legend_l.append("RCP 4.5")
    if utils.rcp85 in rcp_list:
        legend_l.append("RCP 8.5")
    custom_lines = [Line2D([0], [0], color=cols[utils.ref], lw=4)]
    if utils.rcp26 in rcp_list:
        custom_lines.append(Line2D([0], [0], color=cols[utils.rcp26], lw=4))
    if utils.rcp45 in rcp_list:
        custom_lines.append(Line2D([0], [0], color=cols[utils.rcp45], lw=4))
    if utils.rcp85 in rcp_list:
        custom_lines.append(Line2D([0], [0], color=cols[utils.rcp85], lw=4))
    ax.legend(custom_lines, legend_l, loc="upper left", frameon=False)
    plt.ylim(y_min, y_max)
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