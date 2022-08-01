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

# Dashboard libraries.
import cl_auth
import cl_rcp
import cl_sim
import dash_plot
import dash_utils as du
from cl_constant import const as c
from cl_context import cntx
from cl_delta import Delta, Deltas
from cl_hor import Hor, Hors
from cl_lib import Lib, Libs
from cl_project import Project, Projects
from cl_rcp import RCP, RCPs
from cl_sim import Sim, Sims
from cl_stat import Stat, Stats
from cl_varidx import VarIdx, VarIdxs
from cl_view import View, Views

# List of projects accessible to the user.
# This is initially a string (items separated by semi-columns), then it becomes an array of strings.
project_l = ""


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

    global project_l

    # Initialize context.
    cntx.code = c.PLATFORM_STREAMLIT
    cntx.views = Views()
    cntx.libs = Libs()
    cntx.deltas = Deltas(["False", "True"])
    cntx.delta = Delta("False")
    cntx.varidxs = VarIdxs()
    cntx.hors = Hors()
    cntx.rcps = RCPs()

    # Logo.
    st.sidebar.image(cntx.load_image(p=cntx.p_logo), width=150)
    st.sidebar.write("Portail de visualisation de scénarios et d'indices climatiques (v" + str(c.VERSION) + ")")

    # Projects.
    if ";" in project_l:
        project_l = project_l.split(";")
    cntx.projects = Projects(project_l)

    # A place holder (ph) is created, but emptied after loading files.
    # The only way to load files again is to reload the webpage.
    if (cntx.df_files is None) or ((cntx.df_files is not None) and (len(cntx.df_files) == 0)):
        ph_files = st.sidebar.empty()
        with ph_files.form("form_files"):
            st.write("Chargement en cours...")
            cntx.load_files()
        ph_files.empty()

    # Load global configuration file.
    cntx.load()

    project_f = st.sidebar.selectbox("Choisir le projet", options=cntx.projects.desc_l)
    project_code = cntx.projects.code_from_desc(project_f) if cntx.projects is not None else ""
    cntx.project = Project(project_code)
    if c.DBG and c.DBG_PROJECT_CODE != "":
        cntx.project = Project(c.DBG_PROJECT_CODE)

    # Load project-specific configuration file.
    cntx.load()

    # Views.
    cntx.views = Views("*")
    view_f = st.sidebar.radio("Choisir la vue", cntx.views.desc_l)
    view_code = cntx.views.code_from_desc(view_f) if cntx.views is not None else ""
    cntx.view = View(view_code)
    if c.DBG and c.DBG_VIEW_CODE != "":
        cntx.view = View(c.DBG_VIEW_CODE)

    # Plotting libraries.
    cntx.libs = Libs("*")
    if cntx.opt_lib:
        lib_f = st.sidebar.radio("Choisir la librairie visuelle", options=cntx.libs.desc_l)
        lib_code = cntx.libs.code_from_desc(lib_f) if cntx.libs is not None else ""
    else:
        lib_code = c.LIB_HV
        if cntx.view.code == c.VIEW_TBL:
            lib_code = c.LIB_PLY
    cntx.lib = Lib(lib_code)
    if c.DBG and c.DBG_LIB_CODE != "":
        cntx.lib = Lib(c.DBG_LIB_CODE)

    # Deltas.
    cntx.deltas = Deltas("*")
    if (cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP]) and ("True" in cntx.deltas.code_l):
        st.sidebar.markdown("<style>.sel_title {font-size:14.5px}</style>", unsafe_allow_html=True)
        title = "Afficher les anomalies par rapport à la période " + str(cntx.per_ref[0]) + "-" + str(cntx.per_ref[1])
        st.sidebar.markdown("<p class='sel_title'>" + title + "</p>", unsafe_allow_html=True)
        delta_f = st.sidebar.checkbox("", value=False)
        cntx.delta = Delta(str(delta_f))
    else:
        cntx.delta = Delta("False")
    if c.DBG and c.DBG_DELTA_CODE != "":
        cntx.delta = Delta(c.DBG_DELTA_CODE)

    # Variables and indices.
    cntx.varidxs = VarIdxs("*")
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP, c.VIEW_CYCLE, c.VIEW_TAYLOR]:
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
    if c.DBG and c.DBG_VI_CODE != "":
        cntx.varidx = VarIdx(c.DBG_VI_CODE)

    # Horizons.
    if cntx.view.code in [c.VIEW_TBL, c.VIEW_MAP, c.VIEW_CYCLE]:
        cntx.hors = Hors("*")
        hor_f = st.selectbox("Horizon", options=cntx.hors.code_l)
        cntx.hor = Hor(hor_f)
    if c.DBG and c.DBG_HOR_CODE != "":
        cntx.hor = Hor(c.DBG_HOR_CODE)

    # Emission scenarios.
    cntx.rcps = RCPs("*")
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_MAP, c.VIEW_CYCLE, c.VIEW_CLUSTER]:
        rcp_l = cntx.rcps.desc_l
        if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_CLUSTER]:
            rcp_l = [dict(cl_rcp.code_props())[c.RCPXX][0]] + rcp_l
        hor_code_ref = str(cntx.per_ref[0]) + "-" + str(cntx.per_ref[1])
        if (cntx.view.code in [c.VIEW_MAP, c.VIEW_CYCLE]) and (cntx.hor.code == hor_code_ref):
            rcp_code = c.REF
        else:
            rcp_f = st.selectbox("Scénario d'émissions", options=rcp_l)
            rcp_code = cntx.rcps.code_from_desc(rcp_f) if cntx.rcps is not None else ""
        cntx.rcp = RCP(rcp_code)
    if c.DBG and c.DBG_RCP_CODE != "":
        cntx.rcp = RCP(c.DBG_RCP_CODE)

    # Number of clusters.
    n_cluster = 0
    if cntx.view.code == c.VIEW_CLUSTER:
        n_cluster_min = 1
        n_cluster_max = len(du.get_shared_sims())
        n_cluster_suggested = int(math.ceil(0.2 * float(n_cluster_max)))
        n_cluster = st.number_input("Nombre de groupes", format="%i", min_value=n_cluster_min,
                                    max_value=n_cluster_max, value=n_cluster_suggested)

    # Statistics.
    cntx.stats = Stats("*")
    if cntx.view.code == c.VIEW_MAP:
        if cntx.rcp.code == c.REF:
            cntx.stat = Stat(c.STAT_MEAN)
        else:
            stat_f = st.selectbox("Statistique", options=cntx.stats.desc_l)
            stat_code = cntx.stats.code_from_desc(stat_f) if cntx.stats is not None else ""
            cntx.stat = Stat(stat_code)
    if c.DBG and c.DBG_STAT_CODE != "":
        cntx.stat = Stat(c.DBG_STAT_CODE)

    # Simulations.
    cntx.sims = Sims("*")
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_CYCLE]:
        sim_l = cntx.sims.desc_l
        if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
            sim_l = [dict(cl_sim.code_desc())[c.SIMXX]] + sim_l
        if cntx.rcp.code == c.REF:
            cntx.sim = Sim(c.REF)
        else:
            sim_f = st.selectbox("Simulation", options=sim_l)
            if dict(cl_sim.code_desc())[c.SIMXX] == sim_f:
                sim_code = c.SIMXX
            else:
                sim_code = cntx.sims.code_from_desc(sim_f) if cntx.sims is not None else ""
            cntx.sim = Sim(sim_code)

    # View: time series.
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
        df_rcp = pd.DataFrame(du.load_data(dash_plot.MODE_RCP))
        df_sim = pd.DataFrame(du.load_data(dash_plot.MODE_SIM))
        if cntx.view.code == c.VIEW_TS:
            if cntx.delta.code == "False":
                st.write("Valeurs ajustées (après ajustement de biais)")
            else:
                st.write("Différence entre les valeurs observées et les valeurs ajustées")
        else:
            if cntx.delta.code == "False":
                st.write("Valeurs non ajustées (avant ajustement de biais)")
            else:
                st.write("Différence entre les valeurs ajustées et les valeurs non ajustées")
        if cntx.lib.code in [c.LIB_ALT, c.LIB_MAT]:
            st.write(dash_plot.gen_ts(df_rcp, dash_plot.MODE_RCP))
            st.write(dash_plot.gen_ts(df_sim, dash_plot.MODE_SIM))
        else:
            if (df_rcp is not None) and len(df_rcp) > 0:
                st.write(hv.render(dash_plot.gen_ts(df_rcp, dash_plot.MODE_RCP)), backend="bokeh")
            if (df_sim is not None) and len(df_sim) > 0:
                st.write(hv.render(dash_plot.gen_ts(df_sim, dash_plot.MODE_SIM)), backend="bokeh")

    # View: statistics table.
    elif cntx.view.code == c.VIEW_TBL:
        st.write(dash_plot.gen_tbl())

    # View: map.
    elif cntx.view.code == c.VIEW_MAP:
        df = pd.DataFrame(du.load_data())
        stats_lower = Stat(c.STAT_CENTILE, cntx.opt_map_centiles[0])
        stats_upper = Stat(c.STAT_CENTILE, cntx.opt_map_centiles[len(cntx.opt_map_centiles) - 1])
        stats = Stats(stats_lower)
        stats.add(stats_upper)
        range_vals = list(du.calc_range(stats.centile_as_str_l))
        if cntx.lib.code == c.LIB_MAT:
            st.write(dash_plot.gen_map(df, range_vals))
        else:
            st.write(hv.render(dash_plot.gen_map(df, range_vals)), backend="bokeh")

    # View: annual cycle.
    elif cntx.view.code == c.VIEW_CYCLE:
        df_ms = pd.DataFrame(du.load_data("MS"))
        if (df_ms is not None) and (len(df_ms) > 0):
            cycle_ms = dash_plot.gen_cycle_ms(df_ms)
            if cntx.lib.code == c.LIB_MAT:
                st.write(cycle_ms)
            else:
                st.write(hv.render(cycle_ms), backend="bokeh")
        df_d = pd.DataFrame(du.load_data("D"))
        if (df_d is not None) and (len(df_d) > 0):
            cycle_d = dash_plot.gen_cycle_d(df_d)
            if cntx.lib.code == c.LIB_MAT:
                st.write(cycle_d)
            else:
                st.write(hv.render(cycle_d), backend="bokeh")

    # View: Taylor.
    elif cntx.view.code == c.VIEW_TAYLOR:
        if cntx.varidx.is_var:
            df_regrid = pd.DataFrame(du.load_data("regrid"))
            df_qqmap = pd.DataFrame(du.load_data("qqmap"))
            st.write("Valeurs non ajustées (avant ajustement de biais)")
            st.write(dash_plot.gen_taylor_plot(df_regrid))
            st.write("Valeurs ajustées (après ajustement de biais)")
            st.write(dash_plot.gen_taylor_plot(df_qqmap))
        else:
            df = pd.DataFrame(du.load_data())
            st.write(dash_plot.gen_taylor_plot(df))

    # View: clustering.
    else:
        st.write(dash_plot.gen_cluster_tbl(n_cluster))
        if cntx.varidxs.count in [1, 2]:
            cluster = dash_plot.gen_cluster_plot(n_cluster)
            if cntx.lib.code == c.LIB_MAT:
                st.write(cluster)
            else:
                st.write(hv.render(cluster), backend="bokeh")

    # Reference value.
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TBL]:
        tbl_ref = str(du.ref_val())
        st.write("Valeur moyenne pour la période de référence : " + tbl_ref)


# Create authentication instance.
auth = None
if auth is None:
    auth = cl_auth.Auth()

# Debug mode.
if c.DBG:
    project_l = [c.DBG_PROJECT_CODE]
    refresh()

# Authentication page.
elif (project_l == "") and (cl_auth.force_auth()):

    # A place holder (ph) is created, but removed after a successful authentication.
    # The only way to go back to the authentication page is to reload the webpage.
    ph_auth = st.empty()
    with ph_auth.form("form"):

        # Create form.
        st.image(cntx.load_image(p=cntx.p_logo), width=150)
        st.write("Portail de visualisation d'information climatique (v" + str(c.VERSION) + ")")
        auth.usr = st.text_input("Identifiant")
        auth.pwd = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button(label="Soumettre")

        # Load projects.
        auth.load_projects()
        project_l = auth.projects

        # Display error message.
        if (auth.usr != "") and (auth.pwd != "") and (project_l == ""):
            st.error("Accès refusé!")

    # Remove the placeholder and load main page if the user has access to projects.
    if project_l != "":
        ph_auth.empty()
        refresh()

# Main page.
else:
    auth.load_projects()
    project_l = auth.projects
    refresh()
