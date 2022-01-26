# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: View and Views.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
from typing import List, Union

# Dashboard libraries.
import def_object
from def_constant import const as c
from def_context import cntx


def code_desc(
) -> dict:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and descriptions.

    Returns
    -------
    dict
        Dictionary of codes and descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """

    return {
        c.view_ts:      "Série temporelle",
        c.view_ts_bias: "Série temporelle " +
                        ("(biais)" if cntx.code == c.platform_jupyter else "avant ajustement de biais"),
        c.view_tbl:     "Tableau",
        c.view_map:     "Carte",
        c.view_cycle:   "Cycle annuel",
        c.view_cluster: "Similarité entre les simulations"
    }


class View(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object View.
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

        code = code.split("-")[0]
        desc = "" if code == "" else dict(code_desc())[code]
        super(View, self).__init__(code=code, desc=desc)


class Views(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Views.
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

        super(Views, self).__init__()

        if len(args) > 0:
            if args[0] == "*":
                self.load()
            else:
                self.add(args[0])

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        code_l = []

        # The items are extracted from directory names. They must be comprised in 'code_desc'.
        # ~/<project_code>/*
        for code in list(dict(code_desc()).keys()):
            if len(list(glob.glob(cntx.d_project + code + "*/"))) > 0:
                code_l.append(code)
        if c.view_ts in code_l:
            code_l.append(c.view_cluster)

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], View],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[str, List[str]]
            Item (code, list of codes or instance of View).
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, View):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(View(code_l[i]))

        return super(Views, self).add(items, inplace)
