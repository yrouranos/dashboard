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
        c.LIB_ALT: "altair",
        c.LIB_HV:  "hvplot",
        c.LIB_MAT: "matplotlib",
        c.LIB_PLY: "plotly"
    }


class Lib(cl_object.Obj):

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


class Libs(cl_object.Objs):

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
                lib_code = c.LIB_HV
                if cntx.view.code == c.VIEW_TBL:
                    lib_code = c.LIB_PLY
                code_l = [lib_code]
            elif cntx.view.code in [c.VIEW_TS, c.VIEW_TS_BIAS]:
                code_l = [c.LIB_ALT, c.LIB_HV, c.LIB_MAT]
            elif cntx.view.code == c.VIEW_TBL:
                code_l = [c.LIB_PLY]
            elif cntx.view.code in [c.VIEW_MAP, c.VIEW_CYCLE]:
                code_l = [c.LIB_HV, c.LIB_MAT]
            elif cntx.view.code == c.VIEW_CLUSTER:
                code_l = [c.LIB_HV, c.LIB_MAT]
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
