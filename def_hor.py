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

import dash_utils
import def_object
import def_rcp
import def_view
import glob
import os
from typing import Union, List


class Hor(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hor.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    def __init__(self, code):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Hor, self).__init__(code=code, desc=code)


class Hors(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hors.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Hors, self).__init__()

        if len(args) == 1:
            if isinstance(args[0], str) or isinstance(args[0], list):
                self.add(args[0])
            else:
                self.load(args)

    def load(self, args):

        """
        ----------------------------------------
        Load items.

        Parameters
        ----------
        args :
            args[0] = cntx : def_context.Context
                Context.
        ----------------------------------------
        """
        
        cntx = args[0]
        
        code_l = []

        # The items are extracted from directory names.
        # ~/<project_code>/map/<vi_code>/*
        if cntx.view.get_code() == def_view.mode_map:
            p = str(dash_utils.get_d_data(cntx)) + "<view>/<vi_code>/*/*_<delta>.csv"
            p = p.replace("<view>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("_<delta>", "" if cntx.delta is False else "_delta")
            for p in glob.glob(p):
                code = os.path.basename(os.path.dirname(p))
                if code not in code_l:
                    code_l.append(code)

        # The items are extracted from the 'hor' column of data files.
        # ~/<project_code>/tbl/<vi_code>.csv
        elif cntx.view.get_code() == def_view.mode_tbl:
            df = dash_utils.load_data(cntx)
            code_l = list(dict.fromkeys(list(df["hor"])))
            code_l.remove(df[df["rcp"] == def_rcp.rcp_ref]["hor"][0])

        # The items are extracted from directory names.
        # ~/<project_code>/cycle*/*
        elif cntx.view.get_code() == def_view.mode_cycle:
            p = str(dash_utils.get_d_data(cntx)) + "<view>/<vi_code>/*"
            p = p.replace("<view>/", cntx.view.get_code() + "*/")
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            for p_i in list(glob.glob(p)):
                code = os.path.basename(p_i)
                if code not in code_l:
                    code_l.append(code)

        code_l.sort()

        # Remove the items that include all years. For instance, if the horizons are 1981-2010, 2021-2050, 2051-2080
        # and 1981-2080, the last horizon needs to be removed.
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
            items.append(Hor(code_l[i]))
        
        return super(Hors, self).add_items(items, inplace)
