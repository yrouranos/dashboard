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


class Project(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Project.
    --------------------------------------------------------------------------------------------------------------------
    """

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
            self.load_quantiles()
        elif code != "":
            self.quantiles = [-1, -1]

    @property
    def quantiles(
        self
    ):

        """
        ----------------------------------------
        Get quantiles (low and high).

        Returns
        -------
        List[float]
            Quantiles.
        ----------------------------------------
        """

        return self._quantiles

    @quantiles.setter
    def quantiles(
        self,
        quantiles: Optional[List[float]]
    ):

        """
        ----------------------------------------
        Get quantiles (low and high).

        Parameters
        ----------
        quantiles: List[float]
            Quantiles.
        """

        self._quantiles = quantiles

    def load_quantiles(
        self
    ):

        """
        ----------------------------------------
        Get quantiles (low and high).
        ----------------------------------------
        """

        # Codes.
        project_code = cntx.project.code if cntx.project is not None else ""
        view_code = cntx.view.code if cntx.view is not None else ""
        vi_code = cntx.varidx.code if cntx.varidx is not None else ""

        quantiles = []

        # The items are extracted from the 'q' column of data files.
        # ~/<project_code>/tbl/<vi_code>.csv
        if view_code == c.view_tbl:
            df = pd.DataFrame(du.load_data())
            df = df[(df["q"] > 0.01) & (df["q"] < 0.99) & (df["q"] != 0.5)]["q"]
            quantiles = [min(df), max(df)]

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/*/*_q*.csv
        elif view_code == c.view_map:
            p = cntx.d_data + "<project_code>/<view_code>/<vi_code>"
            p = p.replace("<project_code>", project_code)
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p_l = glob.glob(p + "/*/*_q*.csv")
            for p_i in p_l:
                tokens = p_i.replace(".csv", "").replace("_delta", "").split("_q")
                q = float(tokens[len(tokens) - 1])/100
                if q not in quantiles:
                    quantiles.append(q)
            if len(quantiles) > 0:
                quantiles.sort()

        # The items are hardcoded (there must be an even number of cells).
        elif view_code == c.view_cluster:
            quantiles = [0.1, 0.5, 0.9]

        # The items are hardcoded.
        elif view_code in [c.view_ts, c.view_ts_bias]:
            quantiles = [0.0, 1.0]

        self._quantiles = quantiles

    @property
    def quantiles_as_str(
        self
    ) -> List[str]:

        """
        ----------------------------------------
        Get quantiles as string (low and high).

        Returns
        -------
        List[str]
            Formatted quantiles.
        ----------------------------------------
        """

        q_str_l = []
        for i in range(len(self.quantiles)):
            q_str_l.append(str(math.ceil(self.quantiles[i] * 100)))

        return q_str_l


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
