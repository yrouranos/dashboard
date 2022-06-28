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
import cl_gd as gd
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


def oo_structure_local_drive():

    """
    --------------------------------------------------------------------------------------------------------------------
    Test object-oriented structure (local drive).
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


def oo_structure_google_drive(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Test object-oriented structure (Google drive).

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.code = c.PLATFORM_STREAMLIT
    cntx.projects = Projects([project_code])
    cntx.project = Project(project_code)
    cntx.load()

    # Loop through plurial functions.
    for case in ["load_data", "calc_range", "Views", "VarIdxs", "RCPs", "Hors", "Sims", "Stats", "Deltas"]:

        if case == "load_data":
            cntx.view = View(c.VIEW_TBL)
            cntx.varidx = VarIdx(c.V_TASMAX)
            df = pd.DataFrame(du.load_data(c.VIEW_TBL))
            print(df.head())

        elif case == "calc_range":
            cntx.view = View(c.VIEW_MAP)
            vals = du.calc_range(["c010", "c090"])
            print(vals)

        # List views.
        elif case == "Views":
            cntx.views = Views("*")

        # List variables.
        elif case == "VarIdxs":
            for view_code in [c.VIEW_TBL, c.VIEW_TS]:
                cntx.view = View(view_code)
                cntx.varidxs = VarIdxs("*")

        # List RCPs.
        elif case == "RCPs":
            for view_code in [c.VIEW_TBL, c.VIEW_TS, c.VIEW_MAP]:
                cntx.view = View(view_code)
                cntx.varidx = VarIdx(c.V_TASMAX)
                cntx.hor = Hor("2021-2050")
                cntx.rcps = RCPs("*")

        # List horizons.
        elif case == "Hors":
            for view_code in [c.VIEW_MAP, c.VIEW_TBL, c.VIEW_CYCLE]:
                cntx.view = View(view_code)
                cntx.varidx = VarIdx(c.V_TASMAX)
                cntx.hors = Hors("*")

        # List simulations.
        elif case == "Sims":
            for view_code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_CYCLE]:
                cntx.view = View(view_code)
                cntx.varidx = VarIdx(c.V_TASMAX)
                cntx.sims = Sims("*")

        # List statistics.
        elif case == "Stats":
            for view_code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP, c.VIEW_CLUSTER]:
                cntx.view = View(view_code)
                cntx.varidx = VarIdx(c.V_TASMAX)
                cntx.hor = Hor("2021-2050")
                cntx.rcp = RCP(c.RCP45)
                cntx.stats = Stats("*")

        # List deltas.
        elif case == "Deltas":
            for view_code in [c.VIEW_TS, c.VIEW_TS_BIAS, c.VIEW_TBL, c.VIEW_MAP]:
                cntx.view = View(view_code)
                cntx.varidx = VarIdx(c.V_TASMAX)
                cntx.deltas = Deltas("*")


def gen_diagrams(
    project_code: str
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate diagrams.

    Parameters
    ----------
    project_code : str
        Project code.
    --------------------------------------------------------------------------------------------------------------------
    """

    cntx.code = c.PLATFORM_STREAMLIT
    cntx.projects = Projects([project_code])
    cntx.project = Project(project_code)
    cntx.load()
    cntx.views = Views("*")
    gen_ts(project_code, c.VIEW_TS)
    gen_ts(project_code, c.VIEW_TS_BIAS)
    gen_tbl(project_code)
    gen_map(project_code)
    gen_cycle(project_code)
    gen_cluster(project_code)


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
    cntx.stats.add(Stat(c.STAT_CENTILE, cntx.opt_ts_centiles[0]))
    cntx.stats.add(Stat(c.STAT_CENTILE, cntx.opt_ts_centiles[1]))

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

                for mode in [dash_plot.MODE_RCP, dash_plot.MODE_SIM]:

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

    cntx.view = View(c.VIEW_TBL)

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

    cntx.view = View(c.VIEW_MAP)

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
                            z_range = list(du.calc_range(cntx.stats.centile_as_str_l))
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

    cntx.view = View(c.VIEW_CYCLE)
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

    cntx.view = View(c.VIEW_CLUSTER)
    cntx.libs = Libs(cntx.view.code)

    cntx.stats = Stats()
    cntx.stats.add(Stat(c.STAT_CENTILE, cntx.opt_cluster_centiles[0]))
    cntx.stats.add(Stat(c.STAT_CENTILE, cntx.opt_cluster_centiles[1]))

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


def google_drive():

    """
    --------------------------------------------------------------------------------------------------------------------
    Entry point.
    --------------------------------------------------------------------------------------------------------------------
    Structure of test drive:
    +o data
       +o 1
       |  +o 1_a
       |  |  +o 1_a_i
       |  |  +o 1_a_ii
       |  |  +o 1_a_iii
       |  |  +- 1_a_f1
       |  +o 1_b
       |  +o 1_c
       +o 2
       +o 3
       +o 4
       +- 0_f1
       +- 0_f2.ini
       +- 0_f3.csv
       +- 0_f4.geojson
    Legend:
      +o = Directory (branch)
      +- = File (leaf)
    --------------------------------------------------------------------------------------------------------------------
    """

    verbose = True

    # ID of directories. This variable is used to specify an alternative root directory (instead of the absolute
    # root_id, which seems to cause trouble).
    data_id             = "1GjAGJYw3e9sSX41LA5Lmk2Ry2NHsOvJC"
    d_1_id              = "12QNBqFBRmn16fqT-4qqnt7FyvqKgN5la"
    d_1_a_id            = "1yt2ZhySaacc7vHoSPmFOpBglIWuHqOn0"
    d_1_a_f1_id         = "1NlrgUiStIgASxqbJ02mTEu2yl3krt78lmmqOJ3G-bRY"
    d_2_id              = "1KrQo0uELb6EaTmrbk-Ybb6z_FvrNlcmF"
    d_3_id              = "1GNRXsT5OA-ouFZXCy8pl1tq-bBimW2Dv"
    d_4_id              = "1mpxnh8132M3TRnjMa0a6d7qkS2LJHax_"

    # INI file (file ID and name).
    f_0_f2_ini_id       = "1yKGaU_C7eRzlpM85BkXlzmYgtQMoVAct"
    f_0_f2_ini_id_name  = "0_f2.csv"

    # CSV file (file ID and name).
    f_0_f3_csv_id       = "1ABOIbHNKX7dIQHtW1BXm6ZuLVEJHxNbb"
    f_0_f3_csv_id_name  = "0_f3.csv"

    # GEOJSON file (file ID and name).
    f_0_f4_geojson_id   = "1jOEyAZ4gCH1AlJm4H9zyfDBmZgccWpqi"
    f_0_f4_geojson_name = "0_f4.geojson"

    # PNG file (file ID and name).
    f_0_f5_png_id       = "1l4TJrJnQVjYlPJlNd3GA3MGXup3d6A6G"
    f_0_f5_png_name     = "0_f5.png"

    # Create Google Drive service.
    drive = gd.GoogleDrive(data_id)

    # Flat that tells whether to consider only directories (or any item).
    folders_only = False

    # Flag that tells whether to specify base directory or not.
    search_from_base_dir = False

    # Sum up unused to get rid of warnings.
    sink_hole = d_1_a_id + ";" + d_1_a_f1_id + ";" + d_2_id + ";" + d_3_id + ";" + d_4_id + ";" + f_0_f2_ini_id_name +\
        ";" + f_0_f4_geojson_name + ";" + f_0_f5_png_name
    if sink_hole != "":
        sink_hole += ""

    # Perform tests.
    for cmd in ["ls -la", "load_png", "ls -la -R", "ls", "find ls .",
                "glob", "glob_dir_id", "ls -la -R", "path_to_id(folder)",
                "path_to_id(file)", "id_to_path(folder)", "id_to_path(file)", "load_ini", "load_csv", "load_geojson",
                "ls -la", "mkdir", "mkdir", "ls -la", "rm", "ls -la", "id_to_name", "name_to_id"]:

        # Load an image file.
        if cmd == "load_png":
            res = drive.load_image(file_id=f_0_f5_png_id)

        # Load a INI file.
        elif cmd == "load_ini":
            res = drive.load_ini(file_id=f_0_f2_ini_id)

        # Load a CSV file.
        elif cmd == "load_csv":
            res = drive.load_csv(file_id=f_0_f3_csv_id)

        # Load a GEOJSON file.
        elif cmd == "load_geojson":
            res = drive.load_geojson(file_id=f_0_f4_geojson_id)

        # List files (all properties).
        elif cmd in ["ls -la", "ls -la -R"]:
            if folders_only:
                res = drive.ls_la(dir_id=data_id, mime_type=gd.MT_FOLDER, recursive=("-R" in cmd))
            else:
                res = drive.ls_la(dir_id=data_id, recursive=("-R" in cmd))

        # List files (names only).
        elif cmd == "ls":
            if folders_only:
                res = drive.ls(dir_id=data_id, mime_type=gd.MT_FOLDER)
            else:
                res = drive.ls(dir_id=data_id)

        # List files (paths only).
        elif cmd in ["find ls ."]:
            if folders_only:
                res = drive.find_ls_dot(dir_id=data_id, mime_type=gd.MT_FOLDER)
            else:
                res = drive.find_ls_dot(dir_id=data_id)

        # Create directory.
        elif cmd == "mkdir":
            res = drive.mkdir("4", data_id, False)

        # Try to remove a file based on an ID that does not exist.
        elif cmd == "rm":
            res = drive.rm("this_id_does_not_exist")

        # Convert item ID to name.
        elif cmd == "id_to_name":
            res = drive.item_id_to_name(f_0_f3_csv_id)
            # => "0_f3.csv"

        # Convert name to item ID.
        elif cmd == "name_to_id":
            if not search_from_base_dir:
                res = drive.name_to_item_id(name=f_0_f3_csv_id_name)
                # => f_0_f3_csv_id
            else:
                res = drive.name_to_item_id(name=f_0_f3_csv_id_name, dir_id=data_id)
                # => f_0_f3_csv_id

        # Convert path to item ID (the item is a directory).
        elif cmd == "path_to_id(folder)":
            res = drive.path_to_item_id("1/1_a/")
            # => d_1_a_id

        # Convert path to item ID (the item is a file).
        elif cmd == "path_to_id(file)":
            res = drive.path_to_item_id("1/1_a/1_a_f1")
            # => d_1_a_f1_id

        # Convert item ID to path (the item is a directory).
        elif cmd == "id_to_path(folder)":
            res = drive.item_id_to_path(item_id=d_1_id)
            # => "1/"

        # Convert item ID to path (the item is a file).
        elif cmd == "id_to_path(file)":
            res = drive.item_id_to_path(item_id=f_0_f3_csv_id)
            # => "0_f3.csv"

        # Find paths corresponding to a pattern (in a given directory, defined as a path).
        elif cmd == "glob":
            if not search_from_base_dir:
                res = drive.glob(pattern="1/*/*", p="")
                # => "1/1_a/1_a_f1"
            else:
                res = drive.glob(pattern="*/*", p="1/")
                # => "1_a/1_a_f1"

        # Find paths corresponding to a pattern (in a given directory, defined as a directory ID).
        elif cmd == "glob_dir_id":
            if not search_from_base_dir:
                res = drive.glob_dir_id(pattern="1/*/*", dir_id=data_id)
                # => "1/1_a/1_a_f1"
            else:
                res = drive.glob_dir_id(pattern="*/*", dir_id=d_1_id)
                # => "1_a/1_a_f1"

        else:
            res = ""

        # Display result in console.
        if verbose:
            print("\n$ " + cmd)
            res_str = res
            if isinstance(res, pd.DataFrame):
                res_str = res.to_string()
            print(res_str)
            print("")

    return


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

    # Google Drive.
    google_drive()

    # Object-oriented structure (local and Google drives).
    oo_structure_local_drive()
    oo_structure_google_drive(project_code)

    # Generation of diagrams.
    gen_diagrams(project_code)


if __name__ == "__main__":

    run("ci-c")
