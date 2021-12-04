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
import project_def
import rcp_def
import stat_def
import utils
import varidx_def as vi
import view_def
import warnings
from typing import Union, List

warnings.filterwarnings("ignore")

cntx = None
dash, projects, views, libs, deltas, varidxs, hors, rcps, stats = \
    None, None, None, None, None, None, None, None, None


def init_components():

    """
    --------------------------------------------------------------------------------------------------------------------
    Initialize components.
    --------------------------------------------------------------------------------------------------------------------
    """

    global projects, views, libs, deltas, varidxs, hors, rcps, stats

    # Projects.
    projects = pn.Column(pn.pane.Markdown("<b>Choisir le projet</b>"),
                         pnw.RadioBoxGroup(name="RadioBoxGroup", options=[""], inline=False))
    projects[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Views.
    views = pn.Column(pn.pane.Markdown("<b>Choisir la vue</b>"),
                      pnw.RadioBoxGroup(name="RadioBoxGroup", options=[""], inline=False))
    views[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Libraries.
    libs = pn.Column(pn.pane.Markdown("<b>Choisir la librairie graphique</b>"),
                     pnw.RadioBoxGroup(name="RadioBoxGroup", options=[""], inline=False))
    libs[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Deltas
    deltas = pn.Column(pn.pane.Markdown("<b>Afficher les anomalies</b>"),
                       pnw.Checkbox(value=False))
    deltas[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Variables and indices.
    varidxs = pn.Column(pn.pane.Markdown("<b>Variable or index</b>"),
                        pnw.Select(options=[""], width=250))
    varidxs[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Horizons.
    hors = pn.Column(pn.pane.Markdown("<b>Horizon</b>"),
                     pnw.Select(options=[""], width=100))
    hors[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Emission scenarios.
    rcps = pn.Column(pn.pane.Markdown("<b>Scénario d'émission</b>"),
                     pnw.Select(options=[""], width=250))
    rcps[1].param.watch(field_updated, ["value"], onlychanged=True)

    # Statistics.
    stats = pn.Column(pn.pane.Markdown("<b>Statistique</b>"),
                      pnw.Select(options=[""], width=250))
    stats[1].param.watch(field_updated, ["value"], onlychanged=True)


def field_updated(event):
    """
    --------------------------------------------------------------------------------------------------------------------
    Field updated.
    --------------------------------------------------------------------------------------------------------------------
    """

    refresh()


def refresh(i: int = 1):

    """
    --------------------------------------------------------------------------------------------------------------------
    Refresh GUI.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx
    global dash, projects, views, libs, deltas, varidxs, hors, rcps, stats

    # Initialize context.
    if cntx is None:
        init_components()
        cntx = context_def.Context()
        cntx.platform = "jupyter"
        cntx.views = view_def.Views()
        cntx.libs = lib_def.Libs()
        cntx.varidxs = vi.VarIdxs()
        cntx.hors = hor_def.Hors()
        cntx.rcps = rcp_def.RCPs()

    # Projects.
    cntx.projects = project_def.Projects(cntx=cntx)
    projects_l = cntx.projects.get_desc_l()
    if projects[1].value not in projects_l:
        projects[1].options = projects_l
        projects[1].value = projects_l[0]
    cntx.project = project_def.Project(code=projects[1].value, cntx=cntx)

    # Views.
    cntx.views = view_def.Views(cntx)
    views_l = cntx.views.get_desc_l()
    if views[1].value not in views_l:
        views[1].options = views_l
        views[1].value = views_l[0]
    cntx.view = view_def.View(cntx.views.get_code(views[1].value))

    # Libraries.
    cntx.libs = lib_def.Libs(cntx.view.get_code())
    libs_l = cntx.libs.get_desc_l()
    if libs[1].value not in libs_l:
        libs[1].options = libs_l
        libs[1].value = libs_l[0]
    cntx.lib = lib_def.Lib(cntx.libs.get_code(libs[1].value))

    # Deltas.
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl, view_def.mode_map]:
        cntx.delta = deltas[1].value
    else:
        cntx.delta = False

    # Variables and indices.
    cntx.varidxs = vi.VarIdxs(cntx)
    varidxs_l = cntx.varidxs.get_desc_l()
    if varidxs[1].value not in varidxs_l:
        varidxs[1].options = varidxs_l
        varidxs[1].value = varidxs_l[0]
    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(varidxs[1].value))
    cntx.project.set_quantiles(cntx.project.get_code(), cntx)

    # Horizons.
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        cntx.hors = hor_def.Hors(cntx)
        hors_l = cntx.hors.get_code_l()
        if hors[1].value not in hors_l:
            hors[1].options = hors_l
            hors[1].value = hors_l[0]
        cntx.hor = hor_def.Hor(hors[1].value)
    else:
        cntx.hor = None

    # Emission scenarios.
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_map]:
        cntx.rcps = rcp_def.RCPs(cntx)
        if cntx.view.get_code() == view_def.mode_map:
            rcps_l = cntx.rcps.get_desc_l()
            if rcps[1].value not in rcps_l:
                rcps[1].options = rcps_l
                rcps[1].value = rcps_l[0]
            cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcps[1].value))
    else:
        cntx.rcp = None

    # Statistics.
    if cntx.view.get_code() == view_def.mode_map:
        cntx.stats = stat_def.Stats(cntx)
        stats_l = cntx.stats.get_desc_l()
        if stats[1].value not in stats_l:
            stats[1].options = stats_l
            stats[1].value = stats_l[0]
        cntx.stat = stat_def.Stat(cntx.stats.get_code(stats[1].value))
    else:
        cntx.stat = None

    # Reference value.
    val_ref = pn.Row("\n\nValeur de référence : ", plot.get_ref_val(cntx))

    # Time series.
    tab_ts = None
    if cntx.view.get_code() == view_def.mode_ts:
        tab_ts = pn.Row(pn.Column(varidxs, plot.gen_ts(cntx),
                                  pn.pane.Markdown("<br><br><br>" if cntx.lib.get_code() == lib_def.mode_alt else ""),
                                  val_ref))

    # Table.
    tab_tbl = None
    if cntx.view.get_code() == view_def.mode_tbl:
        tab_tbl = pn.Row(pn.Column(varidxs, hors, pn.Column(plot.gen_tbl(cntx), width=500), val_ref))

    # Map.
    tab_map = None
    if cntx.view.get_code() == view_def.mode_map:
        tab_map = pn.Row(pn.Column(varidxs, hors, rcps, stats, plot.gen_map(cntx)))

    # Box plot.
    tab_box = None
    if cntx.view.get_code() == view_def.mode_box:
        tab_box = pn.Row(pn.Column(varidxs, plot.gen_box(cntx)))

    # Sidebar.
    sidebar = pn.Column(pn.Column(pn.pane.PNG(utils.get_p_logo(cntx), height=50)),
                        projects, views, libs, deltas,
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
        elif cntx.view.get_code() == view_def.mode_map:
            dash[1] = tab_map
        else:
            dash[1] = tab_box

    refresh(i+1)


refresh()
