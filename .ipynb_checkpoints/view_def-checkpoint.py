# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: View and Views.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import config as cf
import object_def
import os
from typing import List, Union

mode_ts = "ts"
mode_tbl = "tbl"
mode_map = "map"

code_desc = {mode_ts: "Série temporelle",
             mode_tbl: "Tableau",
             mode_map: "Carte"}


class View(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object View.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Contructor.
    def __init__(self, code):
        desc = "" if code == "" else code_desc[code]
        super(View, self).__init__(code=code, desc=desc)


class Views(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Views.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Constructors.
    def __init__(self, *args):
        super(Views, self).__init__()
        
        if len(args) == 0:
            self.load()
        elif len(args) == 1:
            self.add(args[0])

    def load(self):

        """
        Load items.
        """

        code_l = []
        for code in list(code_desc.keys()):
            if code == mode_ts:
                d = cf.d_ts
            elif code == mode_tbl:
                d = cf.d_tbl
            else:
                d = cf.d_map
            if os.path.exists(d):
                code_l.append(code)

        self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        Add one or several items.

        Parameters
        ----------
        code : Union[str, List[str]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(View(code_l[i]))

        return super(Views, self).add_items(items, inplace)
