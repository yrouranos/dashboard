# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Project and Projects.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import dash_utils
import def_context
import def_object
import def_stat
import def_view
import glob
import math
from typing import List, Union, Optional


class Project(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Project.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code="",
        cntx: def_context.Context = None
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Project, self).__init__(code=code, desc=code)

        if (cntx is not None) and (cntx.view is not None):
            self.set_quantiles(code, cntx)
        elif code != "":
            self.quantiles = [-1, -1]

    def set_quantiles(
        self,
        code: str,
        cntx: def_context.Context,
        quantiles: Optional[Union[None, List[float]]] = None
    ):

        """
        ----------------------------------------
        Get quantiles (low and high).

        Parameters
        ----------
        code : str
            Code.
        cntx : def_context.Context
            Context.
        quantiles: Optional[Union[None, List[float]]]
            Quantiles
        ----------------------------------------
        """

        if quantiles is None:

            if cntx.view.get_code() in [def_view.mode_map, def_view.mode_tbl]:

                quantiles = []

                # The items are extracted from the 'q' column of data files.
                # ~/<project_code>/tbl/<vi_code>.csv
                if cntx.view.get_code() == def_view.mode_tbl:
                    df = dash_utils.load_data(cntx)
                    df = df[(df["q"] > 0.01) & (df["q"] < 0.99) & (df["q"] != 0.5)]["q"]
                    quantiles = [min(df), max(df)]

                # The items are extracted from file names.
                # ~/<project_code>/map/<vi_code>/*/*_q*.csv
                elif cntx.view.get_code() == def_view.mode_map:
                    p = dash_utils.d_data + "<project_code>/<view_code>/<vi_code>"
                    p = p.replace("<project_code>", code)
                    p = p.replace("<view_code>", cntx.view.get_code())
                    p = p.replace("<vi_code>", cntx.varidx.get_code())
                    p_l = glob.glob(p + "/*/*_q*.csv")
                    for p_i in p_l:
                        tokens = p_i.replace(".csv", "").replace("_delta", "").split("_q")
                        q = float(tokens[len(tokens) - 1])/100
                        if q not in quantiles:
                            quantiles.append(q)
                    if len(quantiles) > 0:
                        quantiles.sort()

            # Does not apply to the other views.
            else:
                quantiles = [0, 1]

        self.quantiles = quantiles
        def_stat.mode_q_low = "q" + self.get_quantiles_as_str()[0]
        def_stat.mode_q_high = "q" + self.get_quantiles_as_str()[1]

    def get_quantiles(
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

        return self.quantiles

    def get_quantiles_as_str(
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

        q_low = str(math.ceil(self.get_quantiles()[0] * 100))
        q_high = str(math.ceil(self.get_quantiles()[1] * 100))

        return [q_low, q_high]


class Projects(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Projects.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code: Union[str, List[str]] = "",
        cntx: def_context.Context = None
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Projects, self).__init__()

        if cntx is not None:
            self.load()
        elif code != "":
            self.add(code, cntx)

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        code_l = dash_utils.list_dir(dash_utils.d_data)
        code_l.sort()

        self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        cntx: Optional[def_context.Context] = None,
        inplace: Optional[bool] = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        code : Union[str, List[str]]
            Code or list of codes.
        cntx: Optional[def_context.Context]
            Context.
        inplace : Optional[bool]
            If True, modifies the current instance.
        ----------------------------------------
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(Project(code_l[i], cntx))

        return super(Projects, self).add_items(items, inplace)
