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
from def_constant import const as c
from def_context import cntx
from def_delta import Delta
from def_hor import Hor, Hors
from def_lib import Lib, Libs
from def_project import Project, Projects
from def_rcp import RCP, RCPs
from def_sim import Sim, Sims
from def_stat import Stat, Stats
from def_varidx import VarIdx, VarIdxs
from def_view import View, Views


def oo_structure():

    """
    --------------------------------------------------------------------------------------------------------------------
    Test object-oriented structure
    --------------------------------------------------------------------------------------------------------------------
    """

    # Class: Hor.
    hor_code_l = ["1981", 1981, 1981.0, ["1981"], [1981], [1981.0],
                  "1981-2010", ["1981", "2010"], [1981, 2010], [1981.0, 2010.0]]
    for hor_code in hor_code_l:
        hor = Hor(hor_code)
        print("Period " + hor.code + ": " + str(hor.year_1) + " to " + str(hor.year_2))

    # Class: Hors.
    hors = Hors(hor_code_l)
    print(hors.code_l)


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

    cntx.view = View(view_code)
    cntx.libs = Libs(cntx.view.code)

    cntx.stats = Stats()
    cntx.stats.add(Stat(c.stat_centile, cntx.opt_ts_centiles[0]))
    cntx.stats.add(Stat(c.stat_centile, cntx.opt_ts_centiles[1]))

    for lib in cntx.libs.code_l:
        cntx.lib = Lib(lib)

        for delta in ["False", "True"]:
            cntx.delta = Delta(delta)

            cntx.varidxs = VarIdxs("*")
            for varidx in cntx.varidxs.code_l:

                cntx.varidx = VarIdx(varidx)
                cntx.rcps = RCPs("*")
                cntx.rcp = RCP("")
                cntx.sims = Sims("*")
                cntx.sim = Sim("")

                cntx.projects = Projects("*")
                cntx.load()
                cntx.project = Project(project_code)

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

    cntx.view = View(c.view_tbl)

    cntx.libs = Libs(cntx.view.code)
    for lib in cntx.libs.code_l:

        cntx.lib = Lib(lib)

        for delta in ["False", "True"]:
            cntx.delta = Delta(delta)

            cntx.varidxs = VarIdxs("*")
            for varidx in cntx.varidxs.code_l:

                cntx.varidx = VarIdx(varidx)

                cntx.hors = Hors("*")
                for hor in cntx.hors.code_l:

                    cntx.hor = Hor(hor)
                    cntx.rcps = RCPs("*")
                    cntx.projects = Projects("*")
                    cntx.load()
                    cntx.project = Project(project_code)

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

    cntx.view = View(c.view_map)

    cntx.libs = Libs(cntx.view.code)
    for lib in cntx.libs.code_l:

        cntx.lib = Lib(lib)

        for delta in ["False", "True"]:
            cntx.delta = Delta(delta)

            cntx.varidxs = VarIdxs("*")
            for varidx in cntx.varidxs.code_l:

                cntx.varidx = VarIdx(varidx)

                cntx.hors = Hors("*")
                for hor in cntx.hors.code_l:

                    cntx.hor = Hor(hor)

                    cntx.rcps = RCPs("*")
                    for rcp in cntx.rcps.code_l:

                        cntx.rcp = RCP(rcp)
                        cntx.projects = Projects("*")
                        cntx.load()
                        cntx.project = Project(project_code)

                        cntx.stats = Stats("*")
                        for stat in cntx.stats.code_l:

                            cntx.stat = Stat(stat)

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

    cntx.view = View(c.view_cycle)
    cntx.libs = Libs(cntx.view.code)
    cntx.delta = Delta("False")

    for lib in cntx.libs.code_l:

        cntx.lib = Lib(lib)

        cntx.varidxs = VarIdxs("*")
        for varidx in cntx.varidxs.code_l:

            cntx.varidx = VarIdx(varidx)

            cntx.hors = Hors("*")
            for hor in cntx.hors.code_l:

                cntx.hor = Hor(hor)

                cntx.rcps = RCPs("*")
                for rcp in cntx.rcps.code_l:

                    cntx.rcp = RCP(rcp)

                    cntx.sims = Sims("*")
                    for sim in cntx.sims.code_l:
                        cntx.sim = Sim(sim)

                        cntx.projects = Projects("*")
                        cntx.load()
                        cntx.project = Project(project_code)

                        df_ms = pd.DataFrame(du.load_data("MS"))
                        dash_plot.gen_cycle_ms(df_ms)

                        df_d = pd.DataFrame(du.load_data("D"))
                        dash_plot.gen_cycle_d(df_d)


def gen_cluster(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test cluster plot generation.

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.view = View(c.view_cluster)
    cntx.libs = Libs(cntx.view.code)

    cntx.stats = Stats()
    cntx.stats.add(Stat(c.stat_centile, cntx.opt_cluster_centiles[0]))
    cntx.stats.add(Stat(c.stat_centile, cntx.opt_cluster_centiles[1]))

    for lib in cntx.libs.code_l:

        cntx.lib = Lib(lib)

        cntx.delta = Delta("False")

        cntx.varidxs = VarIdxs("*")

        cntx.projects = Projects("*")
        cntx.load()
        cntx.project = Project(project_code)

        n_cluster = 5
        dash_plot.gen_cluster_tbl(n_cluster)
        dash_plot.gen_cluster_plot(n_cluster)


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

    # Object-oriented structure.
    oo_structure()

    # Visual elements.
    cntx.code = c.platform_streamlit
    cntx.project = Project(project_code)
    cntx.views = Views()
    gen_cluster(project_code)
    gen_ts(project_code, c.view_ts)
    gen_ts(project_code, c.view_ts_bias)
    gen_tbl(project_code)
    gen_map(project_code)
    gen_cycle(project_code)
    gen_ts(project_code, c.view_ts_bias)
