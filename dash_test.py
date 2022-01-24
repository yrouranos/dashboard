# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Test functions.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import pandas as pd

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


def gen_ts(
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

    cntx.view = def_view.View(view_code)
    cntx.libs = def_lib.Libs(cntx.view.code)

    for lib in cntx.libs.code_l:
        cntx.lib = def_lib.Lib(lib)

        for delta in ["False", "True"]:
            cntx.delta = def_delta.Delta(delta)

            cntx.varidxs = vi.VarIdxs("*")
            for varidx in cntx.varidxs.code_l:

                cntx.varidx = vi.VarIdx(varidx)
                cntx.rcps = def_rcp.RCPs("*")
                cntx.rcp = def_rcp.RCP("")
                cntx.sims = def_sim.Sims("*")
                cntx.sim = def_sim.Sim("")

                cntx.project.load_quantiles()
                cntx.projects = def_project.Projects("*")
                cntx.project = def_project.Project(project_code)

                for mode in [dash_plot.mode_rcp, dash_plot.mode_sim]:

                    df = pd.DataFrame(du.load_data(mode))
                    dash_plot.gen_ts(df, mode)
                    du.ref_val()


def gen_tbl(
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

    cntx.view = def_view.View(c.view_tbl)

    cntx.libs = def_lib.Libs(cntx.view.code)
    for lib in cntx.libs.code_l:

        cntx.lib = def_lib.Lib(lib)

        for delta in ["False", "True"]:
            cntx.delta = def_delta.Delta(delta)

            cntx.varidxs = vi.VarIdxs("*")
            for varidx in cntx.varidxs.code_l:

                cntx.varidx = vi.VarIdx(varidx)
                cntx.project.load_quantiles()

                cntx.hors = def_hor.Hors("*")
                for hor in cntx.hors.code_l:

                    cntx.hor = def_hor.Hor(hor)
                    cntx.rcps = def_rcp.RCPs("*")
                    cntx.projects = def_project.Projects("*")
                    cntx.project = def_project.Project(project_code)

                    dash_plot.gen_tbl()
                    du.ref_val()


def gen_map(
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

    cntx.view = def_view.View(c.view_map)

    cntx.libs = def_lib.Libs(cntx.view.code)
    for lib in cntx.libs.code_l:

        cntx.lib = def_lib.Lib(lib)

        for delta in ["False", "True"]:
            cntx.delta = def_delta.Delta(delta)

            cntx.varidxs = vi.VarIdxs("*")
            for varidx in cntx.varidxs.code_l:

                cntx.varidx = vi.VarIdx(varidx)
                cntx.project.load_quantiles()

                cntx.hors = def_hor.Hors("*")
                for hor in cntx.hors.code_l:

                    cntx.hor = def_hor.Hor(hor)

                    cntx.rcps = def_rcp.RCPs("*")
                    for rcp in cntx.rcps.code_l:

                        cntx.rcp = def_rcp.RCP(rcp)
                        cntx.projects = def_project.Projects("*")
                        cntx.project = def_project.Project(project_code)

                        cntx.stats = def_stat.Stats("*")
                        for stat in cntx.stats.code_l:

                            cntx.stat = def_stat.Stat(stat)

                            df = pd.DataFrame(du.load_data())
                            z_range = du.calc_range()
                            dash_plot.gen_map(df, z_range)


def gen_cycle(
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

    cntx.view = def_view.View(c.view_cycle)
    cntx.libs = def_lib.Libs(cntx.view.code)
    cntx.delta = def_delta.Delta("False")

    for lib in cntx.libs.code_l:

        cntx.lib = def_lib.Lib(lib)

        cntx.varidxs = vi.VarIdxs("*")
        for varidx in cntx.varidxs.code_l:

            cntx.varidx = vi.VarIdx(varidx)

            cntx.hors = def_hor.Hors("*")
            for hor in cntx.hors.code_l:

                cntx.hor = def_hor.Hor(hor)

                cntx.rcps = def_rcp.RCPs("*")
                for rcp in cntx.rcps.code_l:

                    cntx.rcp = def_rcp.RCP(rcp)

                    cntx.sims = def_sim.Sims("*")
                    for sim in cntx.sims.code_l:
                        cntx.sim = def_sim.Sim(sim)

                        cntx.projects = def_project.Projects("*")
                        cntx.project = def_project.Project(project_code)

                        df_ms = pd.DataFrame(du.load_data("MS"))
                        dash_plot.gen_cycle_ms(df_ms)

                        df_d = pd.DataFrame(du.load_data("D"))
                        dash_plot.gen_cycle_d(df_d)


def run(
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

    cntx.code = c.platform_streamlit
    cntx.project = def_project.Project(project_code)
    cntx.views = def_view.Views()

    gen_ts(project_code, c.view_ts)
    gen_ts(project_code, c.view_ts_bias)
    gen_tbl(project_code)
    gen_map(project_code)
    gen_cycle(project_code)
    gen_ts(project_code, c.view_ts_bias)
