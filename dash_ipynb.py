# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Jupyter-notebook entry point.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import panel as pn
import panel.widgets as pnw
import pandas as pd
import warnings
from typing import List

# Dashboard libraries.
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

warnings.filterwarnings("ignore")

dash, sidebar, project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, sim_f, stat_f, tab_ts, tab_tbl, tab_map,\
    tab_cycle = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
event_cascade = "event_cascade"


def f_code(
    f_name: str
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get field code from its description.

    Parameters
    ----------
    f_name : str
        Field name.

    Returns
    -------
    str
        Field code.
    --------------------------------------------------------------------------------------------------------------------
    """

    code = ""

    if f_name == "project":
        code = project_f[1].value if len(project_f) > 0 else ""
    elif f_name == "view":
        code = cntx.views.code_from_desc(view_f[1].value) if len(view_f) > 0 else ""
    elif f_name == "lib":
        code = cntx.libs.code_from_desc(lib_f[1].value) if len(lib_f) > 0 else ""
    elif f_name == "delta":
        code = delta_f[1].value if len(delta_f) > 0 else "False"
    elif f_name == "varidx":
        code = cntx.varidxs.code_from_desc(varidx_f[1].value) if len(varidx_f) > 0 else ""
    elif f_name == "hor":
        code = cntx.hors.code_from_desc(hor_f[1].value) if len(hor_f) > 0 else ""
    elif f_name == "rcp":
        code = cntx.rcps.code_from_desc(rcp_f[1].value) if len(rcp_f) > 0 else ""
    elif f_name == "stat":
        code = cntx.stats.code_from_desc(stat_f[1].value) if len(stat_f) > 0 else ""
    elif f_name == "sim":
        code = cntx.sims.code_from_desc(sim_f[1].value) if len(sim_f) > 0 else ""

    return code


def update_f(
    f_name: str,
    option_l: List[str] = []
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Update a field.

    This is called to initalize and update GUI components.
    Each field corresponds to a group of two features : a label and a GUI component displaying options. This explains
    why the options are stored into the 2nd sub-component.

    Parameters
    ----------
    f_name : str
        Name of field to update.
    option_l : List[str]
        List of items to add as options.
    --------------------------------------------------------------------------------------------------------------------
    """

    global project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, sim_f, stat_f

    option_l_updated = False

    if f_name == "project":
        if len(project_f) == 0:
            project_f = pn.Column(pn.pane.Markdown("<b>Choisir le projet</b>"),
                                  pnw.Select(options=option_l, width=150))
            project_f[1].param.watch(project_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = project_f[1].value not in option_l
            project_f[1].options = option_l
        if option_l_updated:
            project_f[1].value = project_f[1].options[0]
        cntx.project = Project(str(f_code("project")))

    elif f_name == "view":
        if len(view_f) == 0:
            view_f = pn.Column(pn.pane.Markdown("<b>Choisir la vue</b>"),
                               pnw.RadioBoxGroup(name="RadioBoxGroup", options=option_l, inline=False, ))
            view_f[1].param.watch(view_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = view_f[1].value not in option_l
            view_f[1].options = option_l
        if option_l_updated:
            view_f[1].value = view_f[1].options[0]
        cntx.view = View(str(f_code("view")))

    elif f_name == "lib":
        if len(lib_f) == 0:
            lib_f = pn.Column(pn.pane.Markdown("<b>Choisir la librairie graphique</b>"),
                              pnw.RadioBoxGroup(name="RadioBoxGroup", options=option_l, inline=False))
            lib_f[1].param.watch(lib_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = lib_f[1].value not in option_l
            lib_f[1].options = option_l
        if option_l_updated:
            lib_f[1].value = lib_f[1].options[0]
        cntx.lib = Lib(str(f_code("lib")))

    elif f_name == "delta":
        if len(delta_f) == 0:
            delta_f = pn.Column(pn.pane.Markdown("<b>Afficher les anomalies</b>"),
                                pnw.Checkbox(value=False))
            delta_f[1].param.watch(delta_updated, ["value"], onlychanged=True)
        cntx.delta = Delta(str(f_code("delta")))

    elif f_name == "varidx":
        if len(varidx_f) == 0:
            varidx_f = pn.Column(pn.pane.Markdown("<b>Variable or index</b>"),
                                 pnw.Select(options=option_l, width=700))
            varidx_f[1].param.watch(varidx_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = varidx_f[1].value not in option_l
            varidx_f[1].options = option_l
        if option_l_updated:
            varidx_f[1].value = varidx_f[1].options[0]
        cntx.varidx = VarIdx(str(f_code("varidx")))

    elif f_name == "hor":
        if len(hor_f) == 0:
            hor_f = pn.Column(pn.pane.Markdown("<b>Horizon</b>"),
                              pnw.Select(options=option_l, width=700))
            hor_f[1].param.watch(hor_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = hor_f[1].value not in option_l
            hor_f[1].options = option_l
        if option_l_updated:
            hor_f[1].value = hor_f[1].options[0]
        cntx.hor = Hor(str(f_code("hor")))

    elif f_name == "rcp":
        if len(rcp_f) == 0:
            rcp_f = pn.Column(pn.pane.Markdown("<b>Scénario d'émission</b>"),
                              pnw.Select(options=option_l, width=700))
            rcp_f[1].param.watch(rcp_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = rcp_f[1].value not in option_l
            rcp_f[1].options = option_l
        if option_l_updated:
            rcp_f[1].value = rcp_f[1].options[0]
        cntx.rcp = RCP(str(f_code("rcp")))

    elif f_name == "stat":
        if len(stat_f) == 0:
            stat_f = pn.Column(pn.pane.Markdown("<b>Statistique</b>"),
                               pnw.Select(options=option_l, width=700))
            stat_f[1].param.watch(stat_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = stat_f[1].value not in option_l
            stat_f[1].options = option_l
        if option_l_updated:
            stat_f[1].value = stat_f[1].options[0]
        cntx.stat = Stat(str(f_code("stat")))

    elif f_name == "sim":
        if len(sim_f) == 0:
            sim_f = pn.Column(pn.pane.Markdown("<b>Simulation</b>"),
                              pnw.Select(options=option_l, width=700))
            sim_f[1].param.watch(sim_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = sim_f[1].value not in option_l
            sim_f[1].options = option_l
        if option_l_updated:
            sim_f[1].value = sim_f[1].options[0]
        cntx.sim = Sim(str(f_code("sim")))


def update_sidebar():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update sidebar.
    --------------------------------------------------------------------------------------------------------------------
    """

    global sidebar

    show_delta_f = cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP]
    sidebar = pn.Column(pn.Column(pn.pane.PNG(cntx.p_logo, height=50)),
                        project_f,
                        view_f,
                        lib_f if cntx.opt_lib else None,
                        delta_f if show_delta_f else "",
                        pn.Spacer(background=cntx.col_sb_fill, sizing_mode="stretch_both"),
                        background=cntx.col_sb_fill,
                        width=200)


def update_tab(
    tab_name: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Update dashboard.

    Parameters
    ----------
    tab_name: str
        Tab name.
    --------------------------------------------------------------------------------------------------------------------
    """

    global tab_ts, tab_tbl, tab_map, tab_cycle

    # Reference value.
    ref_val = pn.Row("\n\nValeur moyenne pour la période de référence : ", du.ref_val())

    # Note related to time series.
    if cntx.view.code == c.VIEW_TS:
        if cntx.delta.code == "False":
            ts_note = "Valeurs ajustées (après ajustement de biais)"
        else:
            ts_note = "Différence entre les valeurs observées et les valeurs ajustées"
    else:
        if cntx.delta.code == "False":
            ts_note = "Valeurs non ajustées (avant ajustement de biais)"
        else:
            ts_note = "Différence entre les valeurs ajustées et les valeurs non ajustées"

    if tab_name in c.VIEW_TS:
        df_rcp = pd.DataFrame(du.load_data(dash_plot.MODE_RCP))
        df_sim = pd.DataFrame(du.load_data(dash_plot.MODE_SIM))
        space = pn.pane.Markdown("<br><br><br>" if cntx.lib.code == c.LIB_ALT else "")
        if (df_rcp is not None) and len(df_rcp) > 0:
            ts_rcp = dash_plot.gen_ts(df_rcp, dash_plot.MODE_RCP)
        else:
            ts_rcp = ""
        if (df_sim is not None) and len(df_sim) > 0:
            ts_sim = dash_plot.gen_ts(df_sim, dash_plot.MODE_SIM)
        else:
            ts_sim = ""
        if len(tab_ts) == 0:
            tab_ts = pn.Row(pn.Column(varidx_f,
                                      rcp_f,
                                      sim_f,
                                      ts_note,
                                      ts_rcp,
                                      ts_sim,
                                      space,
                                      ref_val))
        else:
            tab_ts[0][4] = ts_rcp
            tab_ts[0][5] = ts_sim

    elif tab_name == c.VIEW_TBL:
        tbl = dash_plot.gen_tbl()
        if len(tab_tbl) == 0:
            tab_tbl = pn.Row(pn.Column(varidx_f,
                                       hor_f,
                                       pn.Column(tbl, width=700),
                                       ref_val))
        else:
            tab_tbl[0][2][0] = tbl

    elif tab_name == c.VIEW_MAP:
        show_rcp_f = cntx.hor.code != cntx.per_ref_str
        show_stat_f = cntx.hor.code != cntx.per_ref_str
        df = pd.DataFrame(du.load_data())
        z_range = du.calc_range(cntx.stats.centile_as_str_l)
        _map = dash_plot.gen_map(df, z_range)
        if len(tab_map) == 0:
            tab_map = pn.Row(pn.Column(varidx_f,
                                       hor_f,
                                       rcp_f if show_rcp_f else "",
                                       stat_f if show_stat_f else "",
                                       _map))
        else:
            tab_map[0][2] = rcp_f if show_rcp_f else ""
            tab_map[0][3] = stat_f if show_stat_f else ""
            tab_map[0][4] = _map

    elif tab_name == c.VIEW_CYCLE:
        show_rcp_f = cntx.hor.code != cntx.per_ref_str
        show_sim_f = cntx.hor.code != cntx.per_ref_str
        df_ms = pd.DataFrame(du.load_data("MS"))
        df_d = pd.DataFrame(du.load_data("D"))
        cycle_ms = dash_plot.gen_cycle_ms(df_ms)
        cycle_d = dash_plot.gen_cycle_d(df_d)
        if len(tab_cycle) == 0:
            tab_cycle = pn.Row(pn.Column(varidx_f,
                                         hor_f,
                                         rcp_f if show_rcp_f else "",
                                         sim_f if show_sim_f else "",
                                         cycle_ms,
                                         cycle_d))
        else:
            tab_cycle[0][2] = rcp_f if show_rcp_f else ""
            tab_cycle[0][3] = sim_f if show_sim_f else ""
            tab_cycle[0][4] = cycle_ms
            tab_cycle[0][5] = cycle_d


def update_dash():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update dashboard.
    --------------------------------------------------------------------------------------------------------------------
    """

    global dash

    # Initialize sidebar and dashboard.
    if len(dash) == 0:
        update_sidebar()
        dash = pn.Row(sidebar, pn.Column("content", width=500))

    # Update sidebar.
    if cntx.opt_lib:
        dash[0][3] = lib_f
    else:
        dash[0][3] = ""
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP]:
        dash[0][4] = delta_f
    else:
        dash[0][4] = ""

    # Update content.
    # An error occurs if some information is missing; this is expected when launching the application.
    try:
        update_tab(cntx.view.code.replace("_bias", ""))
        if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
            dash[1][0] = tab_ts
        elif cntx.view.code == c.VIEW_TBL:
            dash[1][0] = tab_tbl
        elif cntx.view.code == c.VIEW_MAP:
            dash[1][0] = tab_map
        elif cntx.view.code == c.VIEW_CYCLE:
            dash[1][0] = tab_cycle
    except Exception as e:
        pass


def update_project():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update project.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.projects = Projects("*")
    cntx.load()
    update_f("project", cntx.projects.desc_l)


def update_view():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update view.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.views = Views("*")
    update_f("view", cntx.views.desc_l)


def update_lib():

    """
    --------------------------------------------------------------------------------------------------------------------
    Initialize library.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.libs = Libs("*")
    update_f("lib", cntx.libs.desc_l)


def update_delta():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update delta.
    --------------------------------------------------------------------------------------------------------------------
    """

    update_f("delta", cntx.deltas.desc_l)


def update_varidx():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update variable or index.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.varidxs = VarIdxs("*")
    update_f("varidx", cntx.varidxs.desc_l)


def update_hor():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update horizon.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.view.code in [c.VIEW_TBL, c.VIEW_MAP, c.VIEW_CYCLE]:
        cntx.hors = Hors("*")
        update_f("hor", cntx.hors.desc_l)


def update_rcp():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update emission scenario.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.rcps = RCPs("*")
    rcp_l = cntx.rcps.desc_l
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
        rcp_l = [dict(cl_rcp.code_props())[c.RCPXX][0]] + rcp_l
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_MAP, c.VIEW_CYCLE]:
        update_f("rcp", rcp_l)


def update_stat():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update statistic.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.view.code == c.VIEW_MAP:
        cntx.stats = Stats("*")
        update_f("stat", cntx.stats.desc_l)


def update_sim():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update simulation.
    --------------------------------------------------------------------------------------------------------------------
    """

    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_CYCLE]:
        cntx.sims = Sims("*")
        sim_l = cntx.sims.desc_l
        if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
            sim_l = [dict(cl_sim.code_desc())[c.SIMXX]] + sim_l
        update_f("sim", sim_l)
    if f_code("sim") != "":
        if dict(cl_sim.code_desc())[c.SIMXX] == f_code("sim"):
            sim_code = c.SIMXX
        else:
            sim_code = f_code("sim")
        cntx.sim = Sim(sim_code)


def project_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: project updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    project_code = cntx.projects.code_from_desc(str(f_code("project")))
    cntx.project = Project(project_code)
    cntx.load()

    update_view()
    view_updated()


def view_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: view updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.view = View(str(f_code("view")))

    update_lib()
    lib_updated(event_cascade)
    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP]:
        delta_updated(event_cascade)
    elif cntx.view.code in [c.VIEW_CYCLE]:
        update_varidx()
        varidx_updated()


def lib_updated(event=None):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: library updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.lib = Lib(str(f_code("lib")))

    if event != event_cascade:
        update_dash()


def delta_updated(event=None):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: delta updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.delta = Delta(str(f_code("delta")))

    if cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP]:
        update_varidx()
        varidx_updated()

    if event != event_cascade:
        update_dash()


def varidx_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: variable or index updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.varidx = VarIdx(str(f_code("varidx")))
    cntx.stats = Stats("*")

    if cntx.view.code in [c.VIEW_TBL, c.VIEW_MAP, c.VIEW_CYCLE]:
        update_hor()
        hor_updated()
    elif cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
        update_rcp()
        rcp_updated()


def hor_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: horizon updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.hor = Hor(str(f_code("hor")))

    if cntx.view.code in [c.VIEW_TBL, c.VIEW_MAP, c.VIEW_CYCLE]:
        if cntx.view.code in [c.VIEW_MAP, c.VIEW_CYCLE]:
            update_dash()
        update_rcp()
        rcp_updated()
        if cntx.view.code in [c.VIEW_TBL]:
            update_dash()


def rcp_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: emission scenario updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    if dict(cl_rcp.code_props())[c.RCPXX][0] == f_code("rcp"):
        rcp_code = c.RCPXX
    else:
        rcp_code = f_code("rcp")
    cntx.rcp = RCP(rcp_code)

    if cntx.view.code in [c.VIEW_MAP]:
        update_stat()
        stat_updated()
    elif cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_CYCLE]:
        update_sim()
        sim_updated()


def stat_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: statistoc updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.stat = Stat(str(f_code("stat")))

    update_dash()


def sim_updated():

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: simulation updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.sim = Sim(str(f_code("sim")))

    update_dash()


def main():

    # Initialize context.
    cntx.code    = c.PLATFORM_JUPYTER
    cntx.views   = Views()
    cntx.libs    = Libs()
    cntx.deltas  = Deltas(["False", "True"])
    cntx.delta   = Delta("False")
    cntx.varidxs = VarIdxs()
    cntx.hors    = Hors()
    cntx.rcps    = RCPs()

    # Initialize GUI.
    update_project()
    project_updated()
    update_delta()
    update_dash()
    # display(dash)


main()
