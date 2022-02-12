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
import math
import pandas as pd
import streamlit as st
from PIL import Image

# Dashboard libraries.
import dash_plot
import dash_utils as du
import def_rcp
import def_sim
from def_constant import const as c
from def_context import cntx
from def_delta import Delta, Deltas
from def_hor import Hor, Hors
from def_lib import Lib, Libs
from def_project import Project, Projects
from def_rcp import RCP, RCPs
from def_sim import Sim, Sims
from def_stat import Stat, Stats
from def_varidx import VarIdx, VarIdxs
from def_view import View, Views


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
    cntx.views = Views()
    cntx.libs = Libs()
    cntx.deltas = Deltas(["False", "True"])
    cntx.delta = Delta("False")
    cntx.varidxs = VarIdxs()
    cntx.hors = Hors()
    cntx.rcps = RCPs()

    # Logo.
    st.sidebar.image(Image.open(cntx.p_logo), width=150)

    # Projects.
    cntx.projects = Projects("*")
    project_f = st.sidebar.selectbox("Choisir le projet", options=cntx.projects.desc_l)
    cntx.project = Project(project_f)
    cntx.load()

    # Views.
    cntx.views = Views("*")
    view_f = st.sidebar.radio("Choisir la vue", cntx.views.desc_l)
    view_code = cntx.views.code_from_desc(view_f) if cntx.views is not None else ""
    cntx.view = View(view_code)

    # TODO.Debug view.
    cntx.view = View(c.view_map)

    # Plotting libraries.
    cntx.libs = Libs("*")
    if cntx.opt_lib:
        lib_f = st.sidebar.radio("Choisir la librairie visuelle", options=cntx.libs.desc_l)
        lib_code = cntx.libs.code_from_desc(lib_f) if cntx.libs is not None else ""
    else:
        lib_code = c.lib_hv
        if cntx.view.code == c.view_tbl:
            lib_code = c.lib_ply
    cntx.lib = Lib(lib_code)

    # Deltas.
    cntx.deltas = Deltas("*")
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_tbl, c.view_map]:
        st.sidebar.markdown("<style>.sel_title {font-size:14.5px}</style>", unsafe_allow_html=True)
        title = "Afficher les anomalies par rapport à la période " + str(cntx.per_ref[0]) + "-" + str(cntx.per_ref[1])
        st.sidebar.markdown("<p class='sel_title'>" + title + "</p>", unsafe_allow_html=True)
        delta_f = st.sidebar.checkbox("", value=False)
        cntx.delta = Delta(str(delta_f))
    else:
        cntx.delta = Delta("False")

    # TODO.Debug delta.
    cntx.delta = Delta("True")

    # Variables and indices.
    cntx.varidxs = VarIdxs("*")
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_tbl, c.view_map, c.view_cycle]:
        vi_f = st.selectbox("Variable ou indice", options=cntx.varidxs.desc_l)
        vi_code = cntx.varidxs.code_from_desc(vi_f) if cntx.varidxs is not None else ""
        cntx.varidx = VarIdx(vi_code)
    else:
        st.write("Variable(s)")
        vi_f = []
        vi_code_l = []
        for varidx in cntx.varidxs.items:
            if varidx.is_var:
                vi_f.append(st.checkbox(varidx.desc, value=True))
                vi_code_l.append(varidx.code)
        vi_code_sel_l = []
        for i in range(len(vi_f)):
            if vi_f[i]:
                vi_code_sel_l.append(vi_code_l[i])
        cntx.varidxs = VarIdxs(vi_code_sel_l)

    # Horizons.
    if cntx.view.code in [c.view_tbl, c.view_map, c.view_cycle]:
        cntx.hors = Hors("*")
        hor_f = st.selectbox("Horizon", options=cntx.hors.code_l)
        cntx.hor = Hor(hor_f)

    # Emission scenarios.
    cntx.rcps = RCPs("*")
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_map, c.view_cycle, c.view_cluster]:
        rcp_l = cntx.rcps.desc_l
        if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_cluster]:
            rcp_l = [dict(def_rcp.code_props())[c.rcpxx][0]] + rcp_l
        hor_code_ref = str(cntx.per_ref[0]) + "-" + str(cntx.per_ref[1])
        if (cntx.view.code in [c.view_map, c.view_cycle]) and (cntx.hor.code == hor_code_ref):
            rcp_code = c.ref
        else:
            rcp_f = st.selectbox("Scénario d'émissions", options=rcp_l)
            rcp_code = cntx.rcps.code_from_desc(rcp_f) if cntx.rcps is not None else ""
        cntx.rcp = RCP(rcp_code)

    # Number of clusters.
    n_cluster = 0
    if cntx.view.code == c.view_cluster:
        n_cluster_min = 1
        n_cluster_max = len(du.get_shared_sims())
        n_cluster_suggested = int(math.ceil(0.2 * float(n_cluster_max)))
        n_cluster = st.number_input("Nombre de groupes", format="%i", min_value=n_cluster_min,
                                    max_value=n_cluster_max, value=n_cluster_suggested)

    # Statistics.
    cntx.stats = Stats("*")
    if cntx.view.code == c.view_map:
        if cntx.rcp.code == c.ref:
            cntx.stat = Stat(c.stat_mean)
        else:
            stat_f = st.selectbox("Statistique", options=cntx.stats.desc_l)
            stat_code = cntx.stats.code_from_desc(stat_f) if cntx.stats is not None else ""
            cntx.stat = Stat(stat_code)

    # Simulations.
    cntx.sims = Sims("*")
    if cntx.view.code in [c.view_ts, c.view_ts_bias, c.view_cycle]:
        sim_l = cntx.sims.desc_l
        if cntx.view.code in [c.view_ts, c.view_ts_bias]:
            sim_l = [dict(def_sim.code_desc())[c.simxx]] + sim_l
        if cntx.rcp.code == c.ref:
            cntx.sim = Sim(c.ref)
        else:
            sim_f = st.selectbox("Simulation", options=sim_l)
            if dict(def_sim.code_desc())[c.simxx] == sim_f:
                sim_code = c.simxx
            else:
                sim_code = cntx.sims.code_from_desc(sim_f) if cntx.sims is not None else ""
            cntx.sim = Sim(sim_code)

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
    elif cntx.view.code == c.view_cycle:
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
    else:
        st.write(dash_plot.gen_cluster_tbl(n_cluster))
        if cntx.varidxs.count in [1, 2]:
            cluster = dash_plot.gen_cluster_plot(n_cluster)
            if cntx.lib.code == c.lib_mat:
                st.write(cluster)
            else:
                st.write(hv.render(cluster), backend="bokeh")
    if cntx.view.code in [c.view_ts, c.view_tbl]:
        tbl_ref = str(du.ref_val())
        st.write("Valeur moyenne pour la période de référence : " + tbl_ref)


# Refresh GUI.
refresh()

# Test.
# import dash_test
# dash_test.run("sn")
