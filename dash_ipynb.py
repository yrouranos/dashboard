# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Jupyter-notebook entry point.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import dash_plot
import dash_utils
import def_context
import def_delta
import def_hor
import def_lib
import def_project
import def_rcp
import def_sim
import def_stat
import def_varidx as vi
import def_view
import panel as pn
import panel.widgets as pnw
import warnings
from typing import Union, List

warnings.filterwarnings("ignore")

cntx = None
dash, project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, sim_f, stat_f = \
    None, None, None, None, None, None, None, None, None, None


def update_field(
        field: str,
        option_l: List[str]
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Update a field.

    This is called to initalize and update GUI components.
    Each field corresponds to a group of two features : a label and a GUI component displaying options. This explains
    why the options are stored into the 2nd sub-component.

    Parameters
    ----------
    field : str
        Name of field to update.
    option_l : List[str]
        List of items to add as options.
    --------------------------------------------------------------------------------------------------------------------
    """

    global project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, sim_f, stat_f

    option_l_updated = False
    if field == "project":
        if project_f is None:
            project_f = pn.Column(pn.pane.Markdown("<b>Choisir le projet</b>"),
                                  pnw.Select(options=option_l, width=150))
            project_f[1].param.watch(project_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = project_f[1].value not in option_l
            project_f[1].options = option_l
        if option_l_updated:
            project_f[1].value = project_f[1].options[0]

    elif field == "view":
        if view_f is None:
            view_f = pn.Column(pn.pane.Markdown("<b>Choisir la vue</b>"),
                               pnw.RadioBoxGroup(name="RadioBoxGroup", options=option_l, inline=False))
            view_f[1].param.watch(view_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = view_f[1].value not in option_l
            view_f[1].options = option_l
        if option_l_updated:
            view_f[1].value = view_f[1].options[0]

    elif field == "lib":
        if lib_f is None:
            lib_f = pn.Column(pn.pane.Markdown("<b>Choisir la librairie graphique</b>"),
                              pnw.RadioBoxGroup(name="RadioBoxGroup", options=option_l, inline=False))
            lib_f[1].param.watch(lib_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = lib_f[1].value not in option_l
            lib_f[1].options = option_l
        if option_l_updated:
            lib_f[1].value = lib_f[1].options[0]

    elif field == "delta":
        if delta_f is None:
            delta_f = pn.Column(pn.pane.Markdown("<b>Afficher les anomalies</b>"),
                                pnw.Checkbox(value=False))
            delta_f[1].param.watch(delta_updated, ["value"], onlychanged=True)

    elif field == "varidx":
        if varidx_f is None:
            varidx_f = pn.Column(pn.pane.Markdown("<b>Variable or index</b>"),
                                 pnw.Select(options=option_l, width=700))
            varidx_f[1].param.watch(varidx_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = varidx_f[1].value not in option_l
            varidx_f[1].options = option_l
        if option_l_updated:
            varidx_f[1].value = varidx_f[1].options[0]

    elif field == "hor":
        if hor_f is None:
            hor_f = pn.Column(pn.pane.Markdown("<b>Horizon</b>"),
                              pnw.Select(options=option_l, width=700))
            hor_f[1].param.watch(hor_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = hor_f[1].value not in option_l
            hor_f[1].options = option_l
        if option_l_updated:
            hor_f[1].value = hor_f[1].options[0]

    elif field == "rcp":
        if rcp_f is None:
            rcp_f = pn.Column(pn.pane.Markdown("<b>Scénario d'émission</b>"),
                              pnw.Select(options=option_l, width=700))
            rcp_f[1].param.watch(rcp_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = rcp_f[1].value not in option_l
            rcp_f[1].options = option_l
        if option_l_updated:
            rcp_f[1].value = rcp_f[1].options[0]

    elif field == "stat":
        if stat_f is None:
            stat_f = pn.Column(pn.pane.Markdown("<b>Statistique</b>"),
                               pnw.Select(options=option_l, width=700))
            stat_f[1].param.watch(stat_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = stat_f[1].value not in option_l
            stat_f[1].options = option_l
        if option_l_updated:
            stat_f[1].value = stat_f[1].options[0]

    elif field == "sim":
        if sim_f is None:
            sim_f = pn.Column(pn.pane.Markdown("<b>Simulation</b>"),
                              pnw.Select(options=option_l, width=700))
            sim_f[1].param.watch(sim_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = sim_f[1].value not in option_l
            sim_f[1].options = option_l
        if option_l_updated:
            sim_f[1].value = sim_f[1].options[0]


def init_context():

    """
    --------------------------------------------------------------------------------------------------------------------
    Initialize context.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx

    cntx = def_context.Context(def_context.code_jupyter)
    cntx.views = def_view.Views()
    cntx.libs = def_lib.Libs()
    cntx.varidxs = vi.VarIdxs()
    cntx.hors = def_hor.Hors()
    cntx.rcps = def_rcp.RCPs()


def update_project():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update project.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, project_f

    cntx.projects = def_project.Projects(cntx=cntx)
    project_l = cntx.projects.get_desc_l()
    update_field("project", project_l)
    cntx.project = def_project.Project(code=project_f[1].value, cntx=cntx)


def update_view():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update view.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, view_f

    cntx.views = def_view.Views(cntx)
    view_l = cntx.views.get_desc_l()
    update_field("view", view_l)
    cntx.view = def_view.View(cntx.views.get_code(view_f[1].value))


def update_lib():

    """
    --------------------------------------------------------------------------------------------------------------------
    Initialize library.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, lib_f

    cntx.libs = def_lib.Libs(cntx.view.get_code())
    lib_l = cntx.libs.get_desc_l()
    update_field("lib", lib_l)
    cntx.lib = def_lib.Lib(cntx.libs.get_code(lib_f[1].value))


def update_delta():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update delta.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, delta_f

    update_field("delta", [""])
    cntx.delta = def_delta.Del(delta_f[1].value)


def update_varidx():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update variable or index.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, varidx_f

    cntx.varidxs = vi.VarIdxs(cntx)
    varidx_l = cntx.varidxs.get_desc_l()
    update_field("varidx", varidx_l)
    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(varidx_f[1].value))
    cntx.project.set_quantiles(cntx.project.get_code(), cntx)


def update_hor():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update horizon.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, hor_f

    if cntx.view.get_code() in [def_view.code_tbl, def_view.code_map, def_view.code_cycle]:
        cntx.hors = def_hor.Hors(cntx)
        hor_l = cntx.hors.get_desc_l()
        update_field("hor", hor_l)
    if hor_f is not None:
        cntx.hor = def_hor.Hor(hor_f[1].value)


def update_rcp():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update emission scenario.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, rcp_f

    if cntx.view.get_code() in [def_view.code_ts, def_view.code_map, def_view.code_cycle, def_view.code_ts_bias]:
        cntx.rcps = def_rcp.RCPs(cntx)
        rcp_l = cntx.rcps.get_desc_l()
        if cntx.view.get_code() in [def_view.code_ts, def_view.code_ts_bias]:
            rcp_l = [""] + rcp_l
        update_field("rcp", rcp_l)
    if rcp_f is not None:
        cntx.rcp = def_rcp.RCP(cntx.rcps.get_code(rcp_f[1].value))


def update_stat():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update statistic.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, stat_f

    if cntx.view.get_code() == def_view.code_map:
        cntx.stats = def_stat.Stats(cntx)
        stat_l = cntx.stats.get_desc_l()
        update_field("stat", stat_l)
    if stat_f is not None:
        cntx.stat = def_stat.Stat(cntx.stats.get_code(stat_f[1].value))


def update_sim():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update simulation.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, sim_f

    if cntx.view.get_code() in [def_view.code_ts, def_view.code_cycle, def_view.code_ts_bias]:
        cntx.sims = def_sim.Sims(cntx)
        sim_l = cntx.sims.get_desc_l()
        if cntx.view.get_code() in [def_view.code_ts, def_view.code_ts_bias]:
            sim_l = [""] + sim_l
        update_field("sim", sim_l)
    if sim_f is not None:
        cntx.sim = def_sim.Sim(sim_f[1].value)


def project_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: project updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, project_f

    cntx.project = def_project.Project(code=project_f[1].value, cntx=cntx)
    update_view()
    view_updated(event)


def view_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: view updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, view_f

    cntx.view = def_view.View(cntx.views.get_code(view_f[1].value))
    update_lib()
    lib_updated(event)


def lib_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: library updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, lib_f

    cntx.lib = def_lib.Lib(cntx.libs.get_code(lib_f[1].value))
    update_varidx()
    varidx_updated(event)


def delta_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: delta updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, delta_f

    cntx.delta = def_delta.Del(delta_f[1].value)
    if cntx.view.get_code() in [def_view.code_ts, def_view.code_map]:
        update_hor()
        hor_updated(event)
    else:
        refresh()


def varidx_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: variable or index updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, varidx_f

    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(varidx_f[1].value))
    if cntx.view.get_code() in [def_view.code_tbl, def_view.code_map, def_view.code_cycle]:
        update_hor()
        hor_updated(event)
    elif cntx.view.get_code() in [def_view.code_ts, def_view.code_ts_bias]:
        update_rcp()
        rcp_updated(event)
    else:
        refresh()


def hor_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: horizon updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, hor_f

    if hor_f is not None:
        cntx.hor = def_hor.Hor(hor_f[1].value)
    if cntx.view.get_code() in [def_view.code_map, def_view.code_cycle]:
        update_rcp()
        rcp_updated(event)
    else:
        refresh()


def rcp_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: emission scenario updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, rcp_f

    cntx.rcp = def_rcp.RCP(cntx.rcps.get_code(rcp_f[1].value))
    if cntx.view.get_code() in [def_view.code_tbl, def_view.code_map]:
        update_stat()
        stat_updated(event)
    elif cntx.view.get_code() in [def_view.code_ts, def_view.code_cycle, def_view.code_ts_bias]:
        update_sim()
        sim_updated(event)
    else:
        refresh()


def stat_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: statistoc updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, stat_f

    cntx.stat = def_stat.Stat(cntx.stats.get_code(stat_f[1].value))
    refresh()


def sim_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: simulation updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, sim_f

    cntx.sim = def_sim.Sim(cntx.sims.get_code(sim_f[1].value))
    refresh()


def refresh():

    """
    --------------------------------------------------------------------------------------------------------------------
    Assemble and refresh GUI.

    The flow is described in dash.py.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, dash, project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, stat_f, sim_f

    # Initialize the context and fields.
    if cntx is None:
        init_context()
        update_project()
        update_view()
        update_lib()
        update_delta()
        update_varidx()
        update_hor()
        update_rcp()
        update_sim()

    # Reference value.
    ref_val = pn.Row("\n\nValeur de référence : ", dash_plot.get_ref_val(cntx))

    # Note related to time series.
    if cntx.view.get_code() == def_view.code_ts:
        if not cntx.delta.get_code():
            ts_note = "Valeurs ajustées (après l'ajustement de biais)"
        else:
            ts_note = "Différence entre les valeurs observées et les valeurs ajustées"
    else:
        if not cntx.delta.get_code():
            ts_note = "Valeurs non ajustées (avant l'ajustement de biais)"
        else:
            ts_note = "Différence entre les valeurs non ajustées et les valeurs ajustées"

    # Tab: time series.
    tab_ts = None
    if cntx.view.get_code() in [def_view.code_ts, def_view.code_ts_bias]:
        df_rcp = dash_utils.load_data(cntx, dash_plot.mode_rcp)
        df_sim = dash_utils.load_data(cntx, dash_plot.mode_sim)
        space = pn.pane.Markdown("<br><br><br>" if cntx.lib.get_code() == def_lib.mode_alt else "")
        tab_ts = pn.Row(pn.Column(varidx_f, rcp_f, sim_f, ts_note,
                                  dash_plot.gen_ts(cntx, df_rcp, dash_plot.mode_rcp),
                                  dash_plot.gen_ts(cntx, df_sim, dash_plot.mode_sim), space, ref_val))

    # Tab: table.
    tab_tbl = None
    if cntx.view.get_code() == def_view.code_tbl:
        tab_tbl = pn.Row(pn.Column(varidx_f, hor_f, pn.Column(dash_plot.gen_tbl(cntx), width=500), ref_val))

    # Tab: map.
    tab_map = None
    if cntx.view.get_code() == def_view.code_map:
        cntx.p_bounds = dash_utils.get_p_bounds(cntx)
        cntx.p_locations = dash_utils.get_p_locations(cntx)
        df = dash_utils.load_data(cntx)
        z_range = dash_utils.get_range(cntx)
        tab_map = pn.Row(pn.Column(varidx_f, hor_f, rcp_f, stat_f, dash_plot.gen_map(cntx, df, z_range)))

    # Tab: cycle plots.
    tab_cycle = None
    if cntx.view.get_code() == def_view.code_cycle:
        df_ms = dash_utils.load_data(cntx, "MS")
        df_d = dash_utils.load_data(cntx, "D")
        tab_cycle = pn.Row(pn.Column(varidx_f, hor_f, rcp_f, sim_f,
                                    dash_plot.gen_cycle_ms(cntx, df_ms), dash_plot.gen_cycle_d(cntx, df_d)))

    # Sidebar.
    cntx.deltas = def_delta.Dels(cntx)
    cntx.delta = def_delta.Del(True in cntx.deltas.get_code_l())
    show_delta_f = cntx.delta.get_code()
    sidebar = pn.Column(pn.Column(pn.pane.PNG(dash_utils.get_p_logo(), height=50)),
                        project_f, view_f, lib_f,
                        delta_f if show_delta_f else "",
                        pn.Spacer(background=cntx.col_sb_fill, sizing_mode="stretch_both"),
                        background=cntx.col_sb_fill,
                        width=200)

    if dash is None:
        dash = pn.Row(sidebar, pn.Column(tab_ts, width=500))
        # display(dash)
    else:
        dash[0] = sidebar
        if cntx.view.get_code() in [def_view.code_ts, def_view.code_ts_bias]:
            dash[1] = tab_ts
        elif cntx.view.get_code() == def_view.code_tbl:
            dash[1] = tab_tbl
        elif cntx.view.get_code() == def_view.code_map:
            dash[1] = tab_map
        else:
            dash[1] = tab_cycle


refresh()
