# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Project and Projects.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
import math
import pandas as pd
from typing import List, Union, Optional

# Dashboard libraries.
import dash_utils as du
import def_object
from def_constant import const as c
from def_context import cntx
from def_stat import Stat, Stats


class Project(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Project.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Statistics (to hold centiles).
    _stats = None

    def __init__(
        self,
        code: str = ""
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Project, self).__init__(code=code, desc=code)

        cntx.load()

        if (cntx is not None) and (cntx.view is not None):
            self.load_stats()
        elif code != "":
            self._stats = Stats()
            for _ in range(2):
                self._stats.add(Stat(c.stat_centile, -1))

    @property
    def stats(
        self
    ) -> Stats:

        """
        ----------------------------------------
        Get statistics.

        Returns
        -------
        Stats
            Statistics.
        ----------------------------------------
        """

        return self._stats

    @stats.setter
    def stats(
        self,
        stats: Stats
    ):

        """
        ----------------------------------------
        Set statistics.

        Parameters
        ----------
        stats: Stats
            Statistics.
        ----------------------------------------
        """

        self._stats = stats

    def load_stats(
        self
    ):

        """
        ----------------------------------------
        Get centiles (lower and upper).
        ----------------------------------------
        """

        # Codes.
        project_code = cntx.project.code if cntx.project is not None else ""
        view_code = cntx.view.code if cntx.view is not None else ""
        vi_code = cntx.varidx.code if cntx.varidx is not None else ""

        centile_l = []

        # The items are extracted from the 'centile' column of data files.
        # ~/<project_code>/tbl/<vi_code>.csv
        if view_code == c.view_tbl:
            df = pd.DataFrame(du.load_data())
            df = df[(df[c.stat_centile] > 0.01) & (df[c.stat_centile] < 0.99) &
                    (df[c.stat_centile] != 0.5)][c.stat_centile]
            centile_l = [min(df), max(df)]

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/*/*_c*.csv
        elif view_code == c.view_map:
            p = cntx.d_data + "<project_code>/<view_code>/<vi_code>"
            p = p.replace("<project_code>", project_code)
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p_l = glob.glob(p + "/*/*_c*.csv")
            for p_i in p_l:
                tokens = p_i.replace(".csv", "").replace("_delta", "").split("_c")
                centile = float(tokens[len(tokens) - 1])
                if centile not in centile_l:
                    centile_l.append(centile)
            if len(centile_l) > 0:
                centile_l.sort()

        # The items are hardcoded (there must be an even number of cells).
        elif view_code == c.view_cluster:
            centile_l = cntx.opt_cluster_centiles

        # The items are hardcoded.
        elif view_code in [c.view_ts, c.view_ts_bias]:
            centile_l = cntx.opt_ts_centiles

        self._stats = Stats()
        for s in range(2):
            self._stats.add(Stat(c.stat_centile, centile_l[s]))


class Projects(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Projects.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code: Union[str, List[str]] = ""
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Projects, self).__init__()

        if code == "*":
            self.load()
        elif code != "":
            self.add(code)

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        code_l = du.list_dir(cntx.d_data)
        if isinstance(code_l, List):
            code_l.sort()

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], Project],
        inplace: Optional[bool] = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[str, List[str], Project]
            Item (code, list of codes or instance of Project).
        inplace: Optional[bool]
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, Project):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(Project(code_l[i]))

        return super(Projects, self).add(items, inplace)
