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

import def_context
import def_hor
import def_lib
import def_model
import def_project
import def_rcp
import def_stat
import dash_plot
import dash_utils
import def_varidx as vi
import def_view
import holoviews as hv
import streamlit as st
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
        +-> view (selected) = ts|bias
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
        +-> view (selected) = tbl
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
        +-> view (selected) = cycle_*
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
        cntx = def_context.Context(def_context.code_streamlit)
        cntx.views = def_view.Views()
        cntx.libs = def_lib.Libs()
        cntx.varidxs = vi.VarIdxs()
        cntx.hors = def_hor.Hors()
        cntx.rcps = def_rcp.RCPs()

    st.sidebar.image(Image.open(dash_utils.get_p_logo()), width=150)

    # Projects.
    cntx.projects = def_project.Projects(cntx=cntx)
    project_f = st.sidebar.selectbox("Choisir le projet", options=cntx.projects.get_desc_l())
    cntx.project = def_project.Project(code=project_f, cntx=cntx)

    # Views.
    cntx.views = def_view.Views(cntx)
    view_f = st.sidebar.radio("Choisir la vue", cntx.views.get_desc_l())
    cntx.view = def_view.View(cntx.views.get_code(view_f))

    # Plotting libraries.
    cntx.libs = def_lib.Libs(cntx.view.get_code())
    lib_f = st.sidebar.radio("Choisir la librairie visuelle", options=cntx.libs.get_desc_l())
    cntx.lib = def_lib.Lib(cntx.libs.get_code(lib_f))

    # Deltas.
    if cntx.view.get_code() in [def_view.mode_ts, def_view.mode_tbl, def_view.mode_map]:
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
    if cntx.view.get_code() in [def_view.mode_tbl, def_view.mode_map, def_view.mode_cycle]:
        cntx.hors = def_hor.Hors(cntx)
        hor_f = st.selectbox("Horizon", options=cntx.hors.get_code_l())
        cntx.hor = def_hor.Hor(hor_f)
        
    # Emission scenarios.
    cntx.rcps = def_rcp.RCPs(cntx)
    if cntx.view.get_code() in [def_view.mode_map, def_view.mode_cycle]:
        rcp_f = st.selectbox("Scénario d'émissions", options=cntx.rcps.get_desc_l())
        cntx.rcp = def_rcp.RCP(cntx.rcps.get_code(rcp_f))

    # Statistics.
    if cntx.view.get_code() == def_view.mode_map:
        cntx.stats = def_stat.Stats(cntx)
        stat_f = st.selectbox("Statistique", options=cntx.stats.get_desc_l())
        cntx.stat = def_stat.Stat(cntx.stats.get_code(stat_f))

    # Models.
    if cntx.view.get_code() == def_view.mode_cycle:
        cntx.models = def_model.Models(cntx)
        model_f = st.selectbox("Modèle", options=cntx.models.get_desc_l())
        cntx.model = def_model.Model(cntx.models.get_code(model_f))

    # GUI components.
    if cntx.view.get_code() in [def_view.mode_ts, def_view.mode_bias]:
        df_rcp = dash_utils.load_data(cntx, dash_plot.mode_rcp)
        df_sim = dash_utils.load_data(cntx, dash_plot.mode_sim)
        if cntx.lib.get_code() in [def_lib.mode_alt, def_lib.mode_mat]:
            st.write(dash_plot.gen_ts(cntx, df_rcp, dash_plot.mode_rcp))
            st.write(dash_plot.gen_ts(cntx, df_sim, dash_plot.mode_sim))
        else:
            st.write(hv.render(dash_plot.gen_ts(cntx, df_rcp, dash_plot.mode_rcp)), backend="bokeh")
            st.write(hv.render(dash_plot.gen_ts(cntx, df_sim, dash_plot.mode_sim)), backend="bokeh")
    elif cntx.view.get_code() == def_view.mode_tbl:
        st.write(dash_plot.gen_tbl(cntx))
    elif cntx.view.get_code() == def_view.mode_map:
        cntx.p_bounds = dash_utils.get_p_bounds(cntx)
        cntx.p_locations = dash_utils.get_p_locations(cntx)
        df = dash_utils.load_data(cntx)
        z_range = dash_utils.get_range(cntx)
        if cntx.lib.get_code() == def_lib.mode_mat:
            st.write(dash_plot.gen_map(cntx, df, z_range))
        else:
            st.write(hv.render(dash_plot.gen_map(cntx, df, z_range)), backend="bokeh")
    else:
        df_ms = dash_utils.load_data(cntx, "MS")
        cycle_ms = dash_plot.gen_cycle_ms(cntx, df_ms)
        if cycle_ms is not None:
            if cntx.lib.get_code() == def_lib.mode_mat:
                st.write(cycle_ms)
            else:
                st.write(hv.render(cycle_ms), backend="bokeh")
        df_d = dash_utils.load_data(cntx, "D")
        cycle_d = dash_plot.gen_cycle_d(cntx, df_d)
        if cycle_d is not None:
            if cntx.lib.get_code() == def_lib.mode_mat:
                st.write(cycle_d)
            else:
                st.write(hv.render(cycle_d), backend="bokeh")
    if cntx.view.get_code() in [def_view.mode_ts, def_view.mode_tbl]:
        tbl_ref = dash_plot.get_ref_val(cntx)
        st.write("Valeur de référence : " + tbl_ref)


# import dash_test
# dash_test.test_all("sn-ko")
refresh()
