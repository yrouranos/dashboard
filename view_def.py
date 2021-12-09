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
import context_def
import glob
import object_def
import utils
from typing import List, Union

mode_ts = "ts"
mode_tbl = "tbl"
mode_map = "map"
mode_disp = "disp"

code_desc = {mode_ts: "Série temporelle",
             mode_tbl: "Tableau",
             mode_map: "Carte",
             mode_disp: "Cycle annuel"}


class View(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object View.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, code):

        """
        ----------------------------------------
        Contructor.
        ----------------------------------------
        """

        code = code.split("-")[0]
        desc = "" if code == "" else code_desc[code]
        super(View, self).__init__(code=code, desc=desc)


class Views(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Views.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Views, self).__init__()

        if len(args) > 0:
            if isinstance(args[0], context_def.Context):
                self.load(args)
            else:
                self.add(args[0])

    def load(self, args):

        """
        ----------------------------------------
        Load items.

        Parameters
        ----------
        args :
            args[0] : cntx: context_def.Context
                Context.
        ----------------------------------------
        """

        cntx = args[0]

        code_l = []

        # The items are extracted from directory names. They must be comprised in 'code_desc'.
        # ~/<project_code>/*
        for code in list(code_desc.keys()):
            if len(list(glob.glob(utils.get_d_data(cntx) + code + "*/"))) > 0:
                code_l.append(code)

        self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        code : Union[str, List[str]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(View(code_l[i]))

        return super(Views, self).add_items(items, inplace)
