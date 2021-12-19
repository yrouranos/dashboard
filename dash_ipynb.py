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

import context_def
import dash_plot
import dash_utils
import hor_def
import lib_def
import model_def
import panel as pn
import panel.widgets as pnw
import project_def
import rcp_def
import stat_def
import varidx_def as vi
import view_def
import warnings
from typing import Union, List

warnings.filterwarnings("ignore")

cntx = None
dash, project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, stat_f, model_f = \
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

    global project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, stat_f, model_f

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

    elif field == "model":
        if model_f is None:
            model_f = pn.Column(pn.pane.Markdown("<b>Modèle</b>"),
                                pnw.Select(options=option_l, width=700))
            model_f[1].param.watch(model_updated, ["value"], onlychanged=True)
        else:
            option_l_updated = model_f[1].value not in option_l
            model_f[1].options = option_l
        if option_l_updated:
            model_f[1].value = model_f[1].options[0]


def init_context():

    """
    --------------------------------------------------------------------------------------------------------------------
    Initialize context.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx

    cntx = context_def.Context(context_def.code_jupyter)
    cntx.views = view_def.Views()
    cntx.libs = lib_def.Libs()
    cntx.varidxs = vi.VarIdxs()
    cntx.hors = hor_def.Hors()
    cntx.rcps = rcp_def.RCPs()


def update_project():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update project.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, project_f

    cntx.projects = project_def.Projects(cntx=cntx)
    project_l = cntx.projects.get_desc_l()
    update_field("project", project_l)
    cntx.project = project_def.Project(code=project_f[1].value, cntx=cntx)


def update_view():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update view.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, view_f

    cntx.views = view_def.Views(cntx)
    view_l = cntx.views.get_desc_l()
    update_field("view", view_l)
    cntx.view = view_def.View(cntx.views.get_code(view_f[1].value))


def update_lib():

    """
    --------------------------------------------------------------------------------------------------------------------
    Initialize library.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, lib_f

    cntx.libs = lib_def.Libs(cntx.view.get_code())
    lib_l = cntx.libs.get_desc_l()
    update_field("lib", lib_l)
    cntx.lib = lib_def.Lib(cntx.libs.get_code(lib_f[1].value))


def update_delta():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update delta.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, delta_f

    update_field("delta", [""])
    cntx.delta = delta_f[1].value


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

    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map, view_def.mode_cycle]:
        cntx.hors = hor_def.Hors(cntx)
        hor_l = cntx.hors.get_desc_l()
        update_field("hor", hor_l)
    if hor_f is not None:
        cntx.hor = hor_def.Hor(hor_f[1].value)


def update_rcp():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update emission scenario.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, rcp_f

    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_map, view_def.mode_cycle]:
        cntx.rcps = rcp_def.RCPs(cntx)
        rcp_l = cntx.rcps.get_desc_l()
        update_field("rcp", rcp_l)
    if rcp_f is not None:
        cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcp_f[1].value))


def update_stat():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update statistic.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, stat_f

    if cntx.view.get_code() == view_def.mode_map:
        cntx.stats = stat_def.Stats(cntx)
        stat_l = cntx.stats.get_desc_l()
        update_field("stat", stat_l)
    if stat_f is not None:
        cntx.stat = stat_def.Stat(cntx.stats.get_code(stat_f[1].value))


def update_model():

    """
    --------------------------------------------------------------------------------------------------------------------
    Update model.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, model_f

    if cntx.view.get_code() == view_def.mode_cycle:
        cntx.models = model_def.Models(cntx)
        model_l = cntx.models.get_desc_l()
        update_field("model", model_l)
    if model_f is not None:
        cntx.model = model_def.Model(model_f[1].value)


def project_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: project updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, project_f

    cntx.project = project_def.Project(code=project_f[1].value, cntx=cntx)
    update_view()
    view_updated(event)


def view_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: view updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, view_f

    cntx.view = view_def.View(cntx.views.get_code(view_f[1].value))
    update_lib()
    lib_updated(event)


def lib_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: library updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, lib_f

    cntx.lib = lib_def.Lib(cntx.libs.get_code(lib_f[1].value))
    update_varidx()
    varidx_updated(event)


def delta_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: delta updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, delta_f

    cntx.delta = delta_f[1].value
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_map]:
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
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map, view_def.mode_cycle]:
        update_hor()
        hor_updated(event)
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
        cntx.hor = hor_def.Hor(hor_f[1].value)
    if cntx.view.get_code() in [view_def.mode_map, view_def.mode_cycle]:
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

    cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcp_f[1].value))
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        update_stat()
        stat_updated(event)
    elif cntx.view.get_code() == view_def.mode_cycle:
        update_model()
        model_updated(event)
    else:
        refresh()


def stat_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: statistoc updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, stat_f

    cntx.stat = stat_def.Stat(cntx.stats.get_code(stat_f[1].value))
    refresh()


def model_updated(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Event: model updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, model_f

    cntx.model = model_def.Model(cntx.models.get_code(model_f[1].value))
    refresh()


def refresh():

    """
    --------------------------------------------------------------------------------------------------------------------
    Assemble and refresh GUI.

    The flow is described in dash.py.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx, dash, project_f, view_f, lib_f, delta_f, varidx_f, hor_f, rcp_f, stat_f, model_f

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

    # Reference value.
    ref_val = pn.Row("\n\nValeur de référence : ", dash_plot.get_ref_val(cntx))

    # Tab: time series.
    tab_ts = None
    if cntx.view.get_code() == view_def.mode_ts:
        df_rcp = dash_utils.load_data(cntx, dash_plot.mode_rcp)
        df_sim = dash_utils.load_data(cntx, dash_plot.mode_sim)
        space = pn.pane.Markdown("<br><br><br>" if cntx.lib.get_code() == lib_def.mode_alt else "")
        tab_ts = pn.Row(pn.Column(varidx_f,
                                  dash_plot.gen_ts(cntx, df_rcp, dash_plot.mode_rcp),
                                  dash_plot.gen_ts(cntx, df_sim, dash_plot.mode_sim), space, ref_val))

    # Tab: table.
    tab_tbl = None
    if cntx.view.get_code() == view_def.mode_tbl:
        tab_tbl = pn.Row(pn.Column(varidx_f, hor_f, pn.Column(dash_plot.gen_tbl(cntx), width=500), ref_val))

    # Tab: map.
    tab_map = None
    if cntx.view.get_code() == view_def.mode_map:
        cntx.p_bounds = dash_utils.get_p_bounds(cntx)
        cntx.p_locations = dash_utils.get_p_locations(cntx)
        df = dash_utils.load_data(cntx)
        z_range = dash_utils.get_range(cntx)
        tab_map = pn.Row(pn.Column(varidx_f, hor_f, rcp_f, stat_f, dash_plot.gen_map(cntx, df, z_range)))

    # Tab: cycle plots.
    tab_cycle = None
    if cntx.view.get_code() == view_def.mode_cycle:
        df_ms = dash_utils.load_data(cntx, "MS")
        df_d = dash_utils.load_data(cntx, "D")
        tab_cycle = pn.Row(pn.Column(varidx_f, hor_f, rcp_f, model_f,
                                    dash_plot.gen_cycle_ms(cntx, df_ms), dash_plot.gen_cycle_d(cntx, df_d)))

    # Sidebar.
    show_delta_f = cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl, view_def.mode_map]
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
        if cntx.view.get_code() == view_def.mode_ts:
            dash[1] = tab_ts
        elif cntx.view.get_code() == view_def.mode_tbl:
            dash[1] = tab_tbl
        elif cntx.view.get_code() == view_def.mode_map:
            dash[1] = tab_map
        else:
            dash[1] = tab_cycle


refresh()
