import altair as alt
import numpy as np
import pandas as pd
import panel as pn
import panel.widgets as pnw
import streamlit as st
from vega_datasets import data

alt.renderers.enable("default")
pn.extension("vega")

def get_data(var_or_idx: str, feature: str):

    p = "./data/" + feature + "/<var_or_idx>.csv"
    df = pd.read_csv(p.replace("<var_or_idx>", var_or_idx))

    return df

def plot_ts(var: str):

    # var = vars.value
    source = get_data(var, "time_series")
    y_min = np.amin([source["ref"].min(), source["rcp45_min"].min(), source["rcp85_min"].min()])
    y_max = np.amax([source["ref"].max(), source["rcp45_max"].max(), source["rcp85_max"].max()])

    line_rcp45 = alt.Chart(source.reset_index()).mark_line().encode(
        x=alt.X("year",
                axis=alt.Axis(title="Année")),
        y=alt.Y("rcp45_moy",
                scale=alt.Scale(domain=[y_min, y_max]),
                axis=alt.Axis(title="Température")),
        color=alt.value("green"),
        tooltip="rcp45_moy"
    ).interactive()

    line_rcp85 = alt.Chart(source.reset_index()).mark_line().encode(
        x="year",
        y=alt.Y("rcp85_moy", scale=alt.Scale(domain=[y_min, y_max])),
        color=alt.value("red"),
        tooltip="rcp85_moy"
    ).interactive()

    band_rcp45 = alt.Chart(source).mark_area(opacity=0.3).encode(
        x="year",
        y=alt.Y("rcp45_min", scale=alt.Scale(domain=[y_min, y_max])),
        y2="rcp45_max",
        color=alt.value("green")
    )

    band_rcp85 = alt.Chart(source).mark_area(opacity=0.3).encode(
        x="year",
        y=alt.Y("rcp85_min", scale=alt.Scale(domain=[y_min, y_max])),
        y2="rcp85_max",
        color=alt.value("red")
    )

    return (line_rcp45 + line_rcp85 + band_rcp45 + band_rcp85).configure_axis(grid=False)

var_list = ["tasmin", "tasmax", "pr", "evspsbl", "evspsblpot"]
vars = st.selectbox("Variable", options=var_list)
st.write(plot_ts(vars))