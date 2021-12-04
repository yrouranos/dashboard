# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Hor and Hors.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import config as cf
import glob
import object_def
import os
import rcp_def
import utils
import view_def
from typing import Union, List


class Hor(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hor.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    def __init__(self, code):

        """
        Contructor.
        """

        super(Hor, self).__init__(code=code, desc=code)


class Hors(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hors.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

        """
        Contructor.
        """

        super(Hors, self).__init__()

        if len(args) == 1:
            if isinstance(args[0], str) or isinstance(args[0], list):
                self.add(args[0])
            else:
                self.load(args)

    def load(self, args):

        """
        Load items.

        Parameters
        ----------
        args :
            args[0] = cntx : context_def.Context
                Context.
        """
        
        cntx = args[0]
        
        code_l = []

        # List all items.
        if cntx.view.get_code() == view_def.mode_map:
            p = utils.get_d_data(cntx) + "<view>/<varidx_code>/*/*_<delta>.csv"
            p = p.replace("<view>", cntx.view.get_code())
            p = p.replace("<varidx_code>", cntx.varidx.get_code())
            p = p.replace("_<delta>", "" if cntx.delta is False else "_delta")
            p_l = glob.glob(p)
            code_l = []
            for p in p_l:
                code = os.path.basename(os.path.dirname(p))
                if code not in code_l:
                    code_l.append(code)
        elif cntx.view.get_code() == view_def.mode_tbl:
            df = utils.load_data(cntx)
            code_l = list(dict.fromkeys(list(df["hor"])))
            code_l.remove(df[df["rcp"] == rcp_def.rcp_ref]["hor"][0])
        code_l.sort()

        # Remove the items that includes all years.
        if len(code_l) > 0:
            min_yr, max_yr = None, None
            for code in code_l:
                tokens = code.split("-")
                if min_yr is None:
                    min_yr = tokens[0]
                    max_yr = tokens[1]
                else:
                    min_yr = min(min_yr, tokens[0])
                    max_yr = max(max_yr, tokens[1])
            range_yr = min_yr + "-" + max_yr
            if range_yr in code_l:
                code_l.remove(range_yr)

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
            items.append(Hor(code_l[i]))
        
        return super(Hors, self).add_items(items, inplace)
