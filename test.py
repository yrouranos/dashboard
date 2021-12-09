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

import context_def
import hor_def
import lib_def
import model_def
import plot
import project_def
import rcp_def
import stat_def
import varidx_def as vi
import view_def


def test_gen_ts(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test time series generation.

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx = context_def.Context()
    cntx.platform = "streamlit"
    cntx.project = project_def.Project(code=project_code, cntx=cntx)
    cntx.views = view_def.Views()
    cntx.view = view_def.View(view_def.mode_ts)
    cntx.libs = lib_def.Libs(cntx.view.get_code())

    for lib in cntx.libs.get_code_l():
        cntx.lib = lib_def.Lib(lib)

        for delta in [False, True]:
            cntx.delta = delta

            cntx.varidxs = vi.VarIdxs(cntx)
            for varidx in cntx.varidxs.get_code_l():

                cntx.varidx = vi.VarIdx(varidx)
                cntx.rcps = rcp_def.RCPs(cntx)
                cntx.project.set_quantiles(cntx.project.get_code(), cntx)
                cntx.projects = project_def.Projects(cntx=cntx)
                cntx.project = project_def.Project(code=project_code, cntx=cntx)

                plot.gen_ts(cntx)


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

    cntx = context_def.Context()
    cntx.platform = "streamlit"
    cntx.project = project_def.Project(code=project_code, cntx=cntx)
    cntx.views = view_def.Views()
    cntx.view = view_def.View(view_def.mode_tbl)

    cntx.libs = lib_def.Libs(cntx.view.get_code())
    for lib in cntx.libs.get_code_l():

        cntx.lib = lib_def.Lib(lib)

        for delta in [False, True]:
            cntx.delta = delta

            cntx.varidxs = vi.VarIdxs(cntx)
            for varidx in cntx.varidxs.get_code_l():

                cntx.varidx = vi.VarIdx(varidx)
                cntx.project.set_quantiles(cntx.project.get_code(), cntx)

                cntx.hors = hor_def.Hors(cntx)
                for hor in cntx.hors.get_code_l():

                    cntx.hor = hor_def.Hor(hor)
                    cntx.rcps = rcp_def.RCPs(cntx)
                    cntx.projects = project_def.Projects(cntx=cntx)
                    cntx.project = project_def.Project(code=project_code, cntx=cntx)

                    plot.gen_tbl(cntx)


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

    cntx = context_def.Context()
    cntx.platform = "streamlit"
    cntx.project = project_def.Project(code=project_code, cntx=cntx)
    cntx.views = view_def.Views()
    cntx.view = view_def.View(view_def.mode_map)

    cntx.libs = lib_def.Libs(cntx.view.get_code())
    for lib in cntx.libs.get_code_l():

        cntx.lib = lib_def.Lib(lib)

        for delta in [False, True]:
            cntx.delta = delta

            cntx.varidxs = vi.VarIdxs(cntx)
            for varidx in cntx.varidxs.get_code_l():

                cntx.varidx = vi.VarIdx(varidx)
                cntx.project.set_quantiles(cntx.project.get_code(), cntx)

                cntx.hors = hor_def.Hors(cntx)
                for hor in cntx.hors.get_code_l():

                    cntx.hor = hor_def.Hor(hor)

                    cntx.rcps = rcp_def.RCPs(cntx)
                    for rcp in cntx.rcps.get_code_l():

                        cntx.rcp = rcp_def.RCP(rcp)
                        cntx.projects = project_def.Projects(cntx=cntx)
                        cntx.project = project_def.Project(code=project_code, cntx=cntx)

                        cntx.stats = stat_def.Stats(cntx)
                        for stat in cntx.stats.get_code_l():

                            cntx.stat = stat_def.Stat(stat)

                            plot.gen_map(cntx)


def test_gen_disp(
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

    cntx = context_def.Context()
    cntx.platform = "streamlit"
    cntx.project = project_def.Project(code=project_code, cntx=cntx)
    cntx.views = view_def.Views()
    cntx.view = view_def.View(view_def.mode_disp)
    cntx.libs = lib_def.Libs(cntx.view.get_code())
    cntx.delta = False

    for lib in cntx.libs.get_code_l():

        cntx.lib = lib_def.Lib(lib)

        cntx.varidxs = vi.VarIdxs(cntx)
        for varidx in cntx.varidxs.get_code_l():

            cntx.varidx = vi.VarIdx(varidx)

            cntx.hors = hor_def.Hors(cntx)
            for hor in cntx.hors.get_code_l():

                cntx.hor = hor_def.Hor(hor)

                cntx.rcps = rcp_def.RCPs(cntx)
                for rcp in cntx.rcps.get_code_l():

                    cntx.rcp = rcp_def.RCP(rcp)

                    cntx.models = model_def.Models(cntx)
                    for model in cntx.models.get_code_l():
                        cntx.model = model_def.Model(model)

                        cntx.projects = project_def.Projects(cntx=cntx)
                        cntx.project = project_def.Project(code=project_code, cntx=cntx)

                        plot.gen_disp_ms(cntx)
                        plot.gen_disp_d(cntx)


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

    test_gen_ts(project_code)
    test_gen_tbl(project_code)
    test_gen_map(project_code)
    test_gen_disp(project_code)
