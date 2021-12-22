# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Test functions.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import dash_plot
import dash_utils
import def_context
import def_hor
import def_lib
import def_model
import def_project
import def_rcp
import def_stat
import def_varidx as vi
import def_view


def test_gen_ts(
    project_code: str,
    view_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test time series generation.

    Parameters
    ----------
    project_code : str
        Project code.
    view_code : str
        View code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx = def_context.Context(def_context.code_streamlit)
    cntx.project = def_project.Project(code=project_code, cntx=cntx)
    cntx.views = def_view.Views()
    cntx.view = def_view.View(view_code)
    cntx.libs = def_lib.Libs(cntx.view.get_code())

    for lib in cntx.libs.get_code_l():
        cntx.lib = def_lib.Lib(lib)

        for delta in [False, True]:
            cntx.delta = delta

            cntx.varidxs = vi.VarIdxs(cntx)
            for varidx in cntx.varidxs.get_code_l():

                cntx.varidx = vi.VarIdx(varidx)
                cntx.rcps = def_rcp.RCPs(cntx)
                cntx.project.set_quantiles(cntx.project.get_code(), cntx)
                cntx.projects = def_project.Projects(cntx=cntx)
                cntx.project = def_project.Project(code=project_code, cntx=cntx)

                for mode in [dash_plot.mode_rcp, dash_plot.mode_sim]:

                    df = dash_utils.load_data(cntx, mode)
                    dash_plot.gen_ts(cntx, df, mode)


def test_gen_tbl(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test table generation.

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx = def_context.Context(def_context.code_streamlit)
    cntx.project = def_project.Project(code=project_code, cntx=cntx)
    cntx.views = def_view.Views()
    cntx.view = def_view.View(def_view.mode_tbl)

    cntx.libs = def_lib.Libs(cntx.view.get_code())
    for lib in cntx.libs.get_code_l():

        cntx.lib = def_lib.Lib(lib)

        for delta in [False, True]:
            cntx.delta = delta

            cntx.varidxs = vi.VarIdxs(cntx)
            for varidx in cntx.varidxs.get_code_l():

                cntx.varidx = vi.VarIdx(varidx)
                cntx.project.set_quantiles(cntx.project.get_code(), cntx)

                cntx.hors = def_hor.Hors(cntx)
                for hor in cntx.hors.get_code_l():

                    cntx.hor = def_hor.Hor(hor)
                    cntx.rcps = def_rcp.RCPs(cntx)
                    cntx.projects = def_project.Projects(cntx=cntx)
                    cntx.project = def_project.Project(code=project_code, cntx=cntx)

                    dash_plot.gen_tbl(cntx)


def test_gen_map(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test map generation.

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx = def_context.Context(def_context.code_streamlit)
    cntx.project = def_project.Project(code=project_code, cntx=cntx)
    cntx.views = def_view.Views()
    cntx.view = def_view.View(def_view.mode_map)

    cntx.libs = def_lib.Libs(cntx.view.get_code())
    for lib in cntx.libs.get_code_l():

        cntx.lib = def_lib.Lib(lib)

        for delta in [False, True]:
            cntx.delta = delta

            cntx.varidxs = vi.VarIdxs(cntx)
            for varidx in cntx.varidxs.get_code_l():

                cntx.varidx = vi.VarIdx(varidx)
                cntx.project.set_quantiles(cntx.project.get_code(), cntx)

                cntx.hors = def_hor.Hors(cntx)
                for hor in cntx.hors.get_code_l():

                    cntx.hor = def_hor.Hor(hor)

                    cntx.rcps = def_rcp.RCPs(cntx)
                    for rcp in cntx.rcps.get_code_l():

                        cntx.rcp = def_rcp.RCP(rcp)
                        cntx.projects = def_project.Projects(cntx=cntx)
                        cntx.project = def_project.Project(code=project_code, cntx=cntx)

                        cntx.stats = def_stat.Stats(cntx)
                        for stat in cntx.stats.get_code_l():

                            cntx.stat = def_stat.Stat(stat)

                            cntx.p_bounds = dash_utils.get_p_bounds(cntx)
                            cntx.p_locations = dash_utils.get_p_locations(cntx)
                            df = dash_utils.load_data(cntx)
                            z_range = dash_utils.get_range(cntx)
                            dash_plot.gen_map(cntx, df, z_range)


def test_gen_cycle(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test boxplot generation.

    Parameters
    ----------
    project_code : str
        Project code..
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx = def_context.Context(def_context.code_streamlit)
    cntx.project = def_project.Project(code=project_code, cntx=cntx)
    cntx.views = def_view.Views()
    cntx.view = def_view.View(def_view.mode_cycle)
    cntx.libs = def_lib.Libs(cntx.view.get_code())
    cntx.delta = False

    for lib in cntx.libs.get_code_l():

        cntx.lib = def_lib.Lib(lib)

        cntx.varidxs = vi.VarIdxs(cntx)
        for varidx in cntx.varidxs.get_code_l():

            cntx.varidx = vi.VarIdx(varidx)

            cntx.hors = def_hor.Hors(cntx)
            for hor in cntx.hors.get_code_l():

                cntx.hor = def_hor.Hor(hor)

                cntx.rcps = def_rcp.RCPs(cntx)
                for rcp in cntx.rcps.get_code_l():

                    cntx.rcp = def_rcp.RCP(rcp)

                    cntx.models = def_model.Models(cntx)
                    for model in cntx.models.get_code_l():
                        cntx.model = def_model.Model(model)

                        cntx.projects = def_project.Projects(cntx=cntx)
                        cntx.project = def_project.Project(code=project_code, cntx=cntx)

                        df_ms = dash_utils.load_data(cntx, "MS")
                        dash_plot.gen_cycle_ms(cntx, df_ms)

                        df_d = dash_utils.load_data(cntx, "D")
                        dash_plot.gen_cycle_d(cntx, df_d)


def test_all(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Launch all test functions.

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    test_gen_ts(project_code, def_view.mode_ts)
    test_gen_tbl(project_code)
    test_gen_map(project_code)
    test_gen_cycle(project_code)
    test_gen_ts(project_code, def_view.mode_bias)
