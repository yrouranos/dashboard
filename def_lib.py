# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Lib and Libs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import def_object
import def_view
from typing import Union, List

mode_alt = "alt"
mode_hv = "hv"
mode_mat = "mat"
mode_ply = "ply"

code_desc = {mode_alt: "altair",
             mode_hv: "hvplot",
             mode_mat: "matplotlib",
             mode_ply: "plotly"}


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

        desc = "" if code == "" else code_desc[code]
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

        if len(args) == 1:
            code_l = []
            if args[0] in [def_view.code_ts, def_view.code_bias]:
                code_l = [mode_alt, mode_hv, mode_mat]
            elif args[0] == def_view.code_tbl:
                code_l = [mode_ply]
            elif args[0] in [def_view.code_map, def_view.code_cycle]:
                code_l = [mode_hv, mode_mat]
            self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):
        
        """
        ----------------------------------------
        Add one or several items.
        
        Paramters
        ---------
        code : Union[str, List[str]]
            Code or list of codes.
        ----------------------------------------
        """        
        
        code_l = code
        if isinstance(code, str):
            code_l = [code]
        
        items = []
        for i in range(len(code_l)):
            items.append(Lib(code_l[i]))
        
        return super(Libs, self).add_items(items, inplace)
