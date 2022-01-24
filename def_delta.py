# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Del and Dels.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
from typing import Union, List

# Dashboard libraries.
import def_object
from def_constant import const as c
from def_context import cntx


class Delta(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Del.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code: str
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Delta, self).__init__(code=code, desc=str(code))


class Deltas(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Dels.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        *args
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Deltas, self).__init__()

        if len(args) == 1:
            if args[0] == "*":
                self.load()
            else:
                self.add(args[0])

    def load(
        self,
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        code_l = ["False", "False"]

        # Codes.
        view_code = cntx.view.code if cntx.view is not None else ""

        # The items are extracted from file names ('ts' or 'ts_bias' view).
        # ~/<project_code>/<view_code>/<vi_code>/*delta.csv
        if view_code in [c.view_ts, c.view_ts_bias]:

            p = cntx.d_project + "<view_code>/*/*delta.csv"
            p = p.replace("<view_code>", view_code)
            p_l = list(glob.glob(p))
            if len(p_l) > 0:
                code_l = ["False", "True"]

        # The items are always available ('tbl' view).
        elif view_code == c.view_tbl:
            code_l = ["False", "True"]

        # The items are extracted from file names ('map' view).
        elif view_code == c.view_map:
            p = cntx.d_project + "<view_code>/*/*/*delta.csv"
            p = p.replace("<view_code>", view_code)
            p_l = list(glob.glob(p))
            if len(p_l) > 0:
                code_l = ["False", "True"]

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], Delta],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[bool, List[bool], Delta]
            Item (code, list of codes or instance of Delta).
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, Delta):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(Delta(code_l[i]))

        return super(Deltas, self).add(items, inplace)
