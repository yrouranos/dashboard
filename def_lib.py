# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Lib and Libs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
from typing import Union, List

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
        c.lib_alt: "altair",
        c.lib_hv:  "hvplot",
        c.lib_mat: "matplotlib",
        c.lib_ply: "plotly"
    }


class Lib(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Lib.
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

        desc = "" if code == "" else dict(code_desc())[code]
        super(Lib, self).__init__(code=code, desc=desc)


class Libs(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Libs.
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

        super(Libs, self).__init__()

        if (len(args) == 1) and (args[0] == "*"):
            code_l = []
            if not cntx.opt_lib:
                lib_code = c.lib_hv
                if cntx.view.code == c.view_tbl:
                    lib_code = c.lib_ply
                code_l = [lib_code]
            elif cntx.view.code in [c.view_ts, c.view_ts_bias]:
                code_l = [c.lib_alt, c.lib_hv, c.lib_mat]
            elif cntx.view.code == c.view_tbl:
                code_l = [c.lib_ply]
            elif cntx.view.code in [c.view_map, c.view_cycle]:
                code_l = [c.lib_hv, c.lib_mat]
            elif cntx.view.code == c.view_cluster:
                code_l = [c.lib_hv, c.lib_mat]
            self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], Lib],
        inplace: bool = True
    ):
        
        """
        ----------------------------------------
        Add one or several items.
        
        Paramters
        ---------
        item: Union[str, List[str], Lib]
            Item (code, list of codes or instance of Lib).
        ----------------------------------------
        """        

        items = []

        if isinstance(item, Lib):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(Lib(code_l[i]))
        
        return super(Libs, self).add(items, inplace)
