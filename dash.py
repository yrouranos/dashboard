# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Streamlit entry point.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import context_def
import dash_plot
import dash_utils
import holoviews as hv
import hor_def
import lib_def
import model_def
import project_def
import rcp_def
import stat_def
import streamlit as st
import varidx_def as vi
import view_def
from PIL import Image

cntx = None


def refresh():

    """
    --------------------------------------------------------------------------------------------------------------------
    Assemble and refresh GUI.

    Flow:

    project (list) = <detected>
    project (selected) = <user_input>
    |
    +-- view (options) = <detected>
        |
        +-> view (selected) = ts (time series)
        |   |
        |   +-> lib (options) = {altair, hvplot, matplotlib}
        |   |   lib (selected) = <user_input>
        |   +-> delta (selected) = <user_input>
        |   |   |
        |   |   hor (options) = <detected> ----------->----------+
        |   |                                                    |
        |   +-> varidx (options) = <detected>                    ˅
        |       varidx (selected) = <user_input> --------------> figure
        |                                                        reference value
        |
        +-> view (selected) = tbl (table)
        |   |
        |   +-> lib (options) = {plotly}
        |   |   lib (selected) = plotly
        |   +-> delta (selected) = <user_input>
        |   +-> varidx (options) = <detected>
        |       varidx (selected) = <user_input>
        |       |
        |       +-> hor (options) = <detected>
        |           hor (selected) = <user_input> -------------> figure
        |                                                        reference value
        |
        +-- view (selected) = map
        |   |
        |   +-> lib (options) = {hvplot, matplotlib}
        |   |   lib (selected) = <user_input>
        |   +-> delta (selected) = <user_input>
        |   |   |
        |   |   hor (options) = <detected> ----------------------+
        |   |                                                    |
        |   +-> varidx (options) = <detected>                    |
        |       varidx (selected) = <user_input>                 |
        |       |                                                |
        |       +-> hor (options) = <detected>                   |
        |           hor (selected) = <user_input>                |
        |           |                                            |
        |           +-> rcp (options) = <detected>               |
        |               rcp (selected) = <user_input>            |
        |               |                                        |
        |               +-> stat (options) = <detected>          ˅
        |                   stat (selected) = <user_input> ----> figure
        |
        +-> view (selected) = disp (annual cycle)
            |
            +-> lib (options) = {hvplot, matplotlib}
            |   lib (selected) = <user_input>
            +-> varidx (options) = <detected>
                varidx (selected) = <user_input>
                |
                +-> hor (options) = <detected>
                    hor (selected) = <user_input>
                    |
                    +-> rcp (options) = <detected>
                        rcp (selected) = <user_input>
                        |
                        +-> model (options) = <detected>
                            model (selected) = <user_input> ---> figure

    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx

    # Initialize context.
    if cntx is None:
        cntx = context_def.Context(context_def.code_streamlit)
        cntx.views = view_def.Views()
        cntx.libs = lib_def.Libs()
        cntx.varidxs = vi.VarIdxs()
        cntx.hors = hor_def.Hors()
        cntx.rcps = rcp_def.RCPs()

    st.sidebar.image(Image.open(dash_utils.get_p_logo()), width=150)

    # Projects.
    cntx.projects = project_def.Projects(cntx=cntx)
    project_f = st.sidebar.selectbox("Choisir le projet", options=cntx.projects.get_desc_l())
    cntx.project = project_def.Project(code=project_f, cntx=cntx)

    # Views.
    cntx.views = view_def.Views(cntx)
    view_f = st.sidebar.radio("Choisir la vue", cntx.views.get_desc_l())
    cntx.view = view_def.View(cntx.views.get_code(view_f))

    # Plotting libraries.
    cntx.libs = lib_def.Libs(cntx.view.get_code())
    lib_f = st.sidebar.radio("Choisir la librairie visuelle", options=cntx.libs.get_desc_l())
    cntx.lib = lib_def.Lib(cntx.libs.get_code(lib_f))

    # Deltas.
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl, view_def.mode_map]:
        st.sidebar.markdown("<style>.sel_title {font-size:14.5px}</style>", unsafe_allow_html=True)
        st.sidebar.markdown("<p class='sel_title'>Afficher les anomalies</p>", unsafe_allow_html=True)
        delta_f = st.sidebar.checkbox("", value=False)
        cntx.delta = delta_f

    # Variables and indices.
    cntx.varidxs = vi.VarIdxs(cntx)
    vi_f = st.selectbox("Variable ou indice", options=cntx.varidxs.get_desc_l())
    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(vi_f))
    cntx.project.set_quantiles(cntx.project.get_code(), cntx)

    # Horizons.
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map, view_def.mode_cycle]:
        cntx.hors = hor_def.Hors(cntx)
        hor_f = st.selectbox("Horizon", options=cntx.hors.get_code_l())
        cntx.hor = hor_def.Hor(hor_f)
        
    # Emission scenarios.
    cntx.rcps = rcp_def.RCPs(cntx)
    if cntx.view.get_code() in [view_def.mode_map, view_def.mode_cycle]:
        rcp_f = st.selectbox("Scénario d'émissions", options=cntx.rcps.get_desc_l())
        cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcp_f))

    # Statistics.
    if cntx.view.get_code() == view_def.mode_map:
        cntx.stats = stat_def.Stats(cntx)
        stat_f = st.selectbox("Statistique", options=cntx.stats.get_desc_l())
        cntx.stat = stat_def.Stat(cntx.stats.get_code(stat_f))

    # Models.
    if cntx.view.get_code() == view_def.mode_cycle:
        cntx.models = model_def.Models(cntx)
        model_f = st.selectbox("Modèle", options=cntx.models.get_desc_l())
        cntx.model = model_def.Model(cntx.models.get_code(model_f))

    # GUI components.
    if cntx.view.get_code() == view_def.mode_ts:
        df = dash_utils.load_data(cntx)
        if cntx.lib.get_code() in [lib_def.mode_alt, lib_def.mode_mat]:
            st.write(dash_plot.gen_ts(cntx, df))
        else:
            st.write(hv.render(dash_plot.gen_ts(cntx, df)), backend="bokeh")
    elif cntx.view.get_code() == view_def.mode_tbl:
        st.write(dash_plot.gen_tbl(cntx))
    elif cntx.view.get_code() == view_def.mode_map:
        cntx.p_bounds = dash_utils.get_p_bounds(cntx)
        cntx.p_locations = dash_utils.get_p_locations(cntx)
        df = dash_utils.load_data(cntx)
        z_range = dash_utils.get_range(cntx)
        if cntx.lib.get_code() == lib_def.mode_mat:
            st.write(dash_plot.gen_map(cntx, df, z_range))
        else:
            st.write(hv.render(dash_plot.gen_map(cntx, df, z_range)), backend="bokeh")
    else:
        df_ms = dash_utils.load_data(cntx, "MS")
        cycle_ms = dash_plot.gen_cycle_ms(cntx, df_ms)
        if cycle_ms is not None:
            if cntx.lib.get_code() == lib_def.mode_mat:
                st.write(cycle_ms)
            else:
                st.write(hv.render(cycle_ms), backend="bokeh")
        df_d = dash_utils.load_data(cntx, "D")
        cycle_d = dash_plot.gen_cycle_d(cntx, df_d)
        if cycle_d is not None:
            if cntx.lib.get_code() == lib_def.mode_mat:
                st.write(cycle_d)
            else:
                st.write(hv.render(cycle_d), backend="bokeh")
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
        tbl_ref = dash_plot.get_ref_val(cntx)
        st.write("Valeur de référence : " + tbl_ref)


refresh()
