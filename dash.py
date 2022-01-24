# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Streamlit entry point.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import holoviews as hv
import pandas as pd
import streamlit as st
from PIL import Image

# Dashboard libraries.
import dash_plot
import dash_utils as du
import def_delta
import def_hor
import def_lib
import def_project
import def_rcp
import def_sim
import def_stat
import def_varidx as vi
import def_view
from def_constant import const as c
from def_context import cntx


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
        +-> view (selected) = ts|ts_bias
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
                        +-> sim (options) = <detected>
                            sim (selected) = <user_input> ---> figure

    --------------------------------------------------------------------------------------------------------------------
    """

    # Initialize context.
    cntx.code = c.platform_streamlit
    cntx.views = def_view.Views()
    cntx.libs = def_lib.Libs()
    cntx.deltas = def_delta.Deltas(["False", "True"])
    cntx.delta = def_delta.Delta("False")
    cntx.varidxs = vi.VarIdxs()
    cntx.hors = def_hor.Hors()
    cntx.rcps = def_rcp.RCPs()

    # Logo.
    st.sidebar.image(Image.open(cntx.p_logo), width=150)

    # Projects.
    cntx.projects = def_project.Projects("*")
    project_f = st.sidebar.selectbox("Choisir le projet", options=cntx.projects.desc_l)
    cntx.project = def_project.Project(project_f)
    cntx.load()

    # Views.
    cntx.views = def_view.Views("*")
    view_f = st.sidebar.radio("Choisir la vue", cntx.views.desc_l)
    view_code = cntx.views.code_from_desc(view_f) if cntx.views is not None else ""
    cntx.view = def_view.View(view_code)

    # Plotting libraries.
    cntx.libs = def_lib.Libs("*")
    if cntx.opt_lib:
        lib_f = st.sidebar.radio("Choisir la librairie visuelle", options=cntx.libs.desc_l)
        lib_code = cntx.libs.code_from_desc(lib_f) if cntx.libs is not None else ""
    else:
        lib_code = c.lib_hv
        if cntx.view.code == c.view_tbl:
            lib_code = c.lib_ply
    cntx.lib = def_lib.Lib(lib_code)

    # Deltas.
    cntx.deltas = def_delta.Deltas("*")
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_tbl, c.view_map]:
        st.sidebar.markdown("<style>.sel_title {font-size:14.5px}</style>", unsafe_allow_html=True)
        title = "Afficher les anomalies par rapport à la période " + str(cntx.per_ref[0]) + "-" + str(cntx.per_ref[1])
        st.sidebar.markdown("<p class='sel_title'>" + title + "</p>", unsafe_allow_html=True)
        delta_f = st.sidebar.checkbox("", value=False)
        cntx.delta = def_delta.Delta(str(delta_f))
    else:
        cntx.delta = def_delta.Delta("False")

    # Variables and indices.
    cntx.varidxs = vi.VarIdxs("*")
    vi_f = st.selectbox("Variable ou indice", options=cntx.varidxs.desc_l)
    vi_code = cntx.varidxs.code_from_desc(vi_f) if cntx.varidxs is not None else ""
    cntx.varidx = vi.VarIdx(vi_code)
    cntx.project.load_quantiles()

    # Horizons.
    if cntx.view.code in [c.view_tbl, c.view_map, c.view_cycle]:
        cntx.hors = def_hor.Hors("*")
        hor_f = st.selectbox("Horizon", options=cntx.hors.code_l)
        cntx.hor = def_hor.Hor(hor_f)

    # TODO: remove
    cntx.view = def_view.View(c.view_cycle)
    cntx.hor = def_hor.Hor("1981-2010")

    # Emission scenarios.
    cntx.rcps = def_rcp.RCPs("*")
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_map, c.view_cycle]:
        rcp_l = cntx.rcps.desc_l
        if cntx.view.code in [c.view_ts, c.view_ts_bias]:
            rcp_l = [dict(def_rcp.code_props())[c.rcpxx][0]] + rcp_l
        hor_code_ref = str(cntx.per_ref[0]) + "-" + str(cntx.per_ref[1])
        if (cntx.view.code in [c.view_map, c.view_cycle]) and (cntx.hor.code == hor_code_ref):
            rcp_code = c.ref
        else:
            rcp_f = st.selectbox("Scénario d'émissions", options=rcp_l)
            rcp_code = cntx.rcps.code_from_desc(rcp_f) if cntx.rcps is not None else ""
        cntx.rcp = def_rcp.RCP(rcp_code)

    # Statistics.
    if cntx.view.code == c.view_map:
        cntx.stats = def_stat.Stats("*")
        if cntx.rcp.code == c.ref:
            cntx.stat = def_stat.Stat(c.stat_mean)
        else:
            stat_f = st.selectbox("Statistique", options=cntx.stats.desc_l)
            stat_code = cntx.stats.code_from_desc(stat_f) if cntx.stats is not None else ""
            cntx.stat = def_stat.Stat(stat_code)

    # Simulations.
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_cycle]:
        cntx.sims = def_sim.Sims("*")
        sim_l = cntx.sims.desc_l
        if cntx.view.code in [c.view_ts, c.view_ts_bias]:
            sim_l = [dict(def_sim.code_desc())[c.simxx]] + sim_l
        if cntx.rcp.code == c.ref:
            cntx.sim = def_sim.Sim(c.ref)
        else:
            sim_f = st.selectbox("Simulation", options=sim_l)
            if dict(def_sim.code_desc())[c.simxx] == sim_f:
                sim_code = c.simxx
            else:
                sim_code = cntx.sims.code_from_desc(sim_f) if cntx.sims is not None else ""
            cntx.sim = def_sim.Sim(sim_code)

    # GUI components.
    if cntx.view.code in [c.view_ts, c.view_ts_bias]:
        df_rcp = pd.DataFrame(du.load_data(dash_plot.mode_rcp))
        df_sim = pd.DataFrame(du.load_data(dash_plot.mode_sim))
        if cntx.view.code == c.view_ts:
            if cntx.delta.code == "False":
                st.write("Valeurs ajustées (après ajustement de biais)")
            else:
                st.write("Différence entre les valeurs observées et les valeurs ajustées")
        else:
            if cntx.delta.code == "False":
                st.write("Valeurs non ajustées (avant ajustement de biais)")
            else:
                st.write("Différence entre les valeurs non ajustées et les valeurs ajustées")
        if cntx.lib.code in [c.lib_alt, c.lib_mat]:
            st.write(dash_plot.gen_ts(df_rcp, dash_plot.mode_rcp))
            st.write(dash_plot.gen_ts(df_sim, dash_plot.mode_sim))
        else:
            st.write(hv.render(dash_plot.gen_ts(df_rcp, dash_plot.mode_rcp)), backend="bokeh")
            st.write(hv.render(dash_plot.gen_ts(df_sim, dash_plot.mode_sim)), backend="bokeh")
    elif cntx.view.code == c.view_tbl:
        st.write(dash_plot.gen_tbl())
    elif cntx.view.code == c.view_map:
        df = pd.DataFrame(du.load_data())
        range_vals = du.calc_range()
        if cntx.lib.code == c.lib_mat:
            st.write(dash_plot.gen_map(df, range_vals))
        else:
            st.write(hv.render(dash_plot.gen_map(df, range_vals)), backend="bokeh")
    else:
        df_ms = pd.DataFrame(du.load_data("MS"))
        cycle_ms = dash_plot.gen_cycle_ms(df_ms)
        if cycle_ms is not None:
            if cntx.lib.code == c.lib_mat:
                st.write(cycle_ms)
            else:
                st.write(hv.render(cycle_ms), backend="bokeh")
        df_d = pd.DataFrame(du.load_data("D"))
        cycle_d = dash_plot.gen_cycle_d(df_d)
        if cycle_d is not None:
            if cntx.lib.code == c.lib_mat:
                st.write(cycle_d)
            else:
                st.write(hv.render(cycle_d), backend="bokeh")
    if cntx.view.code in [c.view_ts, c.view_tbl]:
        tbl_ref = str(du.ref_val())
        st.write("Valeur moyenne pour la période de référence : " + tbl_ref)


# Refresh GUI.
refresh()

# Test.
# import dash_test
# dash_test.run("sn")
