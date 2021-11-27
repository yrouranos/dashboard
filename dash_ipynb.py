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
import varidx_def as vi
import view_def

dash, views, libs, varidxs, hors, rcps = None, None, None, None, None, None
views_updated, libs_updated, varidxs_updated, hors_updated, rcps_updated = True, True, True, True, True


def views_updated_event(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    View updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global views_updated
    views_updated = True
    refresh()


def libs_updated_event(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Plotting library updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global libs_updated
    libs_updated = True
    refresh()


def varidxs_updated_event(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Variable updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global varidxs_updated
    varidxs_updated = True
    refresh()


def hors_updated_event(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    Horizon updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global hors_updated
    hors_updated = True
    refresh()


def rcps_updated_event(event):

    """
    --------------------------------------------------------------------------------------------------------------------
    RCP updated event.
    --------------------------------------------------------------------------------------------------------------------
    """

    global rcps_updated
    rcps_updated = True
    refresh()


def refresh():

    """
    --------------------------------------------------------------------------------------------------------------------
    Refresh GUI.
    --------------------------------------------------------------------------------------------------------------------
    """

    global dash, views, libs, varidxs, hors, rcps
    global views_updated, libs_updated, varidxs_updated, hors_updated, rcps_updated

    # Initialize context.
    cntx = context_def.Context()

    # Views.
    cntx.views = view_def.Views()
    if views is None:
        views = pnw.RadioBoxGroup(name="RadioBoxGroup", options=cntx.views.get_desc_l(), inline=False)
        views.param.watch(views_updated_event, ["value"], onlychanged=True)
    cntx.view = view_def.View(cntx.views.get_code(views.value))

    # Plotting libraries.
    cntx.libs = lib_def.Libs(cntx.view.get_code())
    if views_updated:
        if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_map]:
            libs = pn.Column(pn.pane.Markdown("<b>Choisir la librairie graphique</b>"),
                             pnw.RadioBoxGroup(name="RadioBoxGroup", options=cntx.libs.get_desc_l(), inline=False))
            libs[1].param.watch(libs_updated_event, ["value"], onlychanged=True)
            if cntx.view.get_code() == view_def.mode_ts:
                cntx.lib = lib_def.Lib(cntx.libs.get_code(libs[1].value))
            else:
                cntx.lib = lib_def.Lib(lib_def.mode_mat)
        else:
            libs = pn.Column("")
            cntx.lib = lib_def.Lib("")

    # Variables and indices.
    cntx.varidxs = vi.VarIdxs(cntx.view)

    if views_updated:
        if varidxs is None:
            varidxs = pnw.Select(options=cntx.varidxs.get_desc_l(), width=250)
            varidxs.param.watch(varidxs_updated_event, ["value"], onlychanged=True)
        else:
            varidxs.options = cntx.varidxs.get_desc_l()
    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(varidxs.value))

    # Horizons.
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        cntx.hors = hor_def.Hors(cntx)
    if views_updated or varidxs_updated:
        hors = pnw.Select(options=cntx.hors.get_code_l(), width=100)
        hors.param.watch(hors_updated_event, ["value"], onlychanged=True)
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        cntx.hor = hor_def.Hor(hors.value)

    # Emission scenarios.
    cntx.rcps = rcp_def.RCPs(cntx, cf.d_data)
    if (views_updated or varidxs_updated or hors_updated) and \
            (cntx.view.get_code() == view_def.mode_map):
        if rcps is None:
            rcps = pnw.Select(options=cntx.rcps.get_desc_l(), width=250)
            rcps.param.watch(rcps_updated_event, ["value"], onlychanged=True)
        else:
            rcps.options = cntx.rcps.get_desc_l()
    if cntx.view.get_code() == view_def.mode_map:
        cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcps.value))

    # Time series.
    tab_ts = None
    if (views_updated or libs_updated or varidxs_updated) and \
       (cntx.view.get_code() == view_def.mode_ts):
        tab_ts = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                                  varidxs,
                                  plot.gen_ts(cntx)))

    # Table.
    tab_tbl = None
    if (views_updated or varidxs_updated or hors_updated) and \
       (cntx.view.get_code() == view_def.mode_tbl):
        tab_tbl = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                                   varidxs,
                                   pn.pane.Markdown("<b>Horizon</b>"),
                                   hors,
                                   pn.Column(plot.gen_tbl(cntx), width=500),
                                   pn.Row("Valeur de référence : ", plot.get_ref_val(cntx))))

    # Map.
    tab_map = None
    if (views_updated or varidxs_updated or hors_updated or rcps_updated) and \
       (cntx.view.get_code() == view_def.mode_map):
        tab_map = pn.Row(pn.Column(pn.pane.Markdown("<b>Variable</b>"),
                                   varidxs,
                                   pn.pane.Markdown("<b>Horizon</b>"),
                                   hors,
                                   pn.pane.Markdown("<b>Scénario d'émission</b>"),
                                   rcps,
                                   plot.gen_map(cntx, "quantile", cf.q_l[0]),
                                   plot.gen_map(cntx, "quantile", cf.q_l[1])))

    # Sidebar.
    sidebar = pn.Column(pn.Column(pn.pane.PNG(cf.p_logo, height=50)),
                        pn.pane.Markdown("<b>Choisir la vue</b>"),
                        views,
                        libs,
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

    views_updated, libs_updated, varidxs_updated, hors_updated, rcps_updated = False, False, False, False, False


refresh()
