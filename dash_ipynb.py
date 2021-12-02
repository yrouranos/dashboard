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

import config as cf
import context_def
import hor_def
import lib_def
import panel as pn
import panel.widgets as pnw
import plot
import rcp_def
import stat_def
import varidx_def as vi
import view_def

cntx = None
dash, views, libs, deltas, varidxs, hors, rcps, stats = \
    None, None, None, None, None, None, None, None
view_updated, lib_updated, delta_updated, varidx_updated, hor_updated, rcp_updated, stat_updated = \
    True, True, True, True, True, True, True


def view_updated_event():

    """
    --------------------------------------------------------------------------------------------------------------------
    View updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global view_updated
    view_updated = True
    refresh()


def lib_updated_event():

    """
    --------------------------------------------------------------------------------------------------------------------
    Plotting library updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global lib_updated
    lib_updated = True
    refresh()


def delta_updated_event():

    """
    --------------------------------------------------------------------------------------------------------------------
    Deltac updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global delta_updated
    delta_updated = True
    refresh()


def varidx_updated_event():

    """
    --------------------------------------------------------------------------------------------------------------------
    Variable updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global varidx_updated
    varidx_updated = True
    refresh()


def hor_updated_event():

    """
    --------------------------------------------------------------------------------------------------------------------
    Horizon updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global hor_updated
    hor_updated = True
    refresh()


def rcp_updated_event():

    """
    --------------------------------------------------------------------------------------------------------------------
    RCP updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global rcp_updated
    rcp_updated = True
    refresh()


def stat_updated_event():
    """
    --------------------------------------------------------------------------------------------------------------------
    Statistic updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global stat_updated
    stat_updated = True
    refresh()


def refresh():

    """
    --------------------------------------------------------------------------------------------------------------------
    Refresh GUI.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx
    global dash, views, libs, deltas, varidxs, hors, rcps, stats
    global view_updated, lib_updated, delta_updated, varidx_updated, hor_updated, rcp_updated, stat_updated

    # Initialize context.
    if cntx is None:
        cntx = context_def.Context()
        cntx.platform = "jupyter"
        cntx.views = view_def.Views()
        cntx.libs = lib_def.Libs()
        cntx.varidxs = vi.VarIdxs()
        cntx.hors = hor_def.Hors()
        cntx.rcps = rcp_def.RCPs()
        cntx.stats = stat_def.Stats()

    # Views.
    cntx.views = view_def.Views()
    if views is None:
        views = pnw.RadioBoxGroup(name="RadioBoxGroup", options=cntx.views.get_desc_l(), inline=False)
        views.param.watch(view_updated_event, ["value"], onlychanged=True)
    cntx.view = view_def.View(cntx.views.get_code(views.value))

    # Plotting libraries.
    cntx.libs = lib_def.Libs(cntx.view.get_code())
    if view_updated:
        libs = pn.Column(pn.pane.Markdown("<b>Choisir la librairie graphique</b>"),
                         pnw.RadioBoxGroup(name="RadioBoxGroup", options=cntx.libs.get_desc_l(), inline=False))
        libs[1].param.watch(lib_updated_event, ["value"], onlychanged=True)
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
        cntx.lib = lib_def.Lib(cntx.libs.get_code(libs[1].value))
    else:
        cntx.lib = lib_def.Lib(lib_def.mode_mat)

    # Deltas.
    if deltas is None:
        deltas = pnw.Checkbox(value=False)
        deltas.param.watch(delta_updated_event, ["value"], onlychanged=True)
    cntx.delta = deltas.value

    # Variables and indices.
    cntx.varidxs = vi.VarIdxs(cntx.view)
    if view_updated:
        if varidxs is None:
            varidxs = pnw.Select(options=cntx.varidxs.get_desc_l(), width=250)
            varidxs.param.watch(varidx_updated_event, ["value"], onlychanged=True)
        else:
            varidxs.options = cntx.varidxs.get_desc_l()
    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(varidxs.value))

    # Horizons.
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        cntx.hors = hor_def.Hors(cntx)
    if view_updated or varidx_updated:
        hors = pnw.Select(options=cntx.hors.get_code_l(), width=100)
        hors.param.watch(hor_updated_event, ["value"], onlychanged=True)
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        cntx.hor = hor_def.Hor(hors.value)

    # Emission scenarios.
    cntx.rcps = rcp_def.RCPs(cntx)
    if (view_updated or varidx_updated or hor_updated) and \
       (cntx.view.get_code() == view_def.mode_map):
        rcps = pnw.Select(options=cntx.rcps.get_desc_l(), width=250)
        rcps.param.watch(rcp_updated_event, ["value"], onlychanged=True)
    if cntx.view.get_code() == view_def.mode_map:
        cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcps.value))

    # Statistics.
    if cntx.view.get_code() == view_def.mode_map:
        cntx.stats = stat_def.Stats(cntx)
    if (view_updated or varidx_updated or hor_updated or rcp_updated) and \
       (cntx.view.get_code() == view_def.mode_map):
        stats = pnw.Select(options=cntx.stats.get_desc_l(), width=250)
        stats.param.watch(stat_updated_event, ["value"], onlychanged=True)
    if cntx.view.get_code() == view_def.mode_map:
        cntx.stat = stat_def.Stat(cntx.stats.get_code(stats.value))

    # Time series.
    tab_ts = None
    if (view_updated or lib_updated or delta_updated or varidx_updated) and \
       (cntx.view.get_code() == view_def.mode_ts):
        tab_ts = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                                  varidxs,
                                  plot.gen_ts(cntx),
                                  pn.pane.Markdown("<br><br><br>" if cntx.lib.get_code() == lib_def.mode_alt else ""),
                                  pn.Row("Valeur de référence : ", plot.get_ref_val(cntx))))

    # Table.
    tab_tbl = None
    if (view_updated or delta_updated or varidx_updated or hor_updated) and \
       (cntx.view.get_code() == view_def.mode_tbl):
        tab_tbl = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                                   varidxs,
                                   pn.pane.Markdown("<b>Horizon</b>"),
                                   hors,
                                   pn.Column(plot.gen_tbl(cntx), width=500),
                                   pn.Row("Valeur de référence : ", plot.get_ref_val(cntx))))

    # Map.
    tab_map = None
    if (view_updated or varidx_updated or delta_updated or hor_updated or rcp_updated or stat_updated) and \
       (cntx.view.get_code() == view_def.mode_map):
        tab_map = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                                   varidxs,
                                   pn.pane.Markdown("<b>Horizon</b>"),
                                   hors,
                                   pn.pane.Markdown("<b>Scénario d'émission</b>"),
                                   rcps,
                                   pn.pane.Markdown("<b>Statistique</b>"),
                                   stats,
                                   plot.gen_map(cntx)))

    # Sidebar.
    sidebar = pn.Column(pn.Column(pn.pane.PNG(cf.p_logo, height=50)),
                        pn.pane.Markdown("<b>Choisir la vue</b>"),
                        views,
                        libs,
                        pn.pane.Markdown("<b>Afficher les anomalies</b>"),
                        deltas,
                        pn.Spacer(background=cf.col_sb_fill, sizing_mode="stretch_both"),
                        background=cf.col_sb_fill,
                        width=200)

    # Dashboard.
    if dash is None:
        dash = pn.Row(sidebar, tab_ts)
    else:
        dash[0] = sidebar
        if cntx.view.get_code() == view_def.mode_ts:
            dash[1] = tab_ts
        elif cntx.view.get_code() == view_def.mode_tbl:
            dash[1] = tab_tbl
        else:
            dash[1] = tab_map

    view_updated, lib_updated, delta_updated, varidx_updated, hor_updated, rcp_updated, stat_updated = \
        False, False, False, False, False, False, False


refresh()
