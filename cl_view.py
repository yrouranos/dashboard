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
from typing import List, Union

# Dashboard libraries.
import cl_gd
import cl_object
from cl_constant import const as c
from cl_context import cntx


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
        c.VIEW_TS:      "Série temporelle",
        c.VIEW_TS_BIAS: "Série temporelle " +
                        ("(biais)" if cntx.code == c.PLATFORM_JUPYTER else "avant ajustement de biais"),
        c.VIEW_TBL:     "Tableau",
        c.VIEW_MAP:     "Carte",
        c.VIEW_CYCLE:   "Cycle annuel",
        c.VIEW_CLUSTER: "Similarité entre les simulations",
        c.VIEW_TAYLOR:  "Diagramme de Taylor"
    }


class View(cl_object.Obj):

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


class Views(cl_object.Objs):

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

            pattern = cntx.project.code + "/" + code + "/"

            p_l = list(cntx.files(pattern)[cl_gd.PROP_PATH])
            if len(p_l) > 0:
                code_l.append(code)

        # Add the 'cluster' view (it's using the same data at the 'ts' view).
        if c.VIEW_TS in code_l:

            pattern = cntx.project.code + "/" + c.VIEW_TS + "/*/*_sim.csv"

            f_l = list(cntx.files(pattern)[cl_gd.PROP_PATH])
            if len(f_l) > 0:
                code_l.append(c.VIEW_CLUSTER)

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
