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
import context_def
import object_def
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
    
    # Contructor.
    def __init__(self, code):
        super().__init__(code)
        self.code = code

    def copy(
        self
    ):
        
        """
        Copy item.
        
        Returns
        -------
        Hor
            Copy of item.
        """
        
        return Hor(self.code)


class Hors(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hors.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Constructors.
    def __init__(self, *args):
        super().__init__()

        if len(args) == 1:
            if isinstance(args[0], context_def.Context):
                self.load(args)
            else:
                self.items = self.add(args[0]).items

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
            p = cf.d_map + "<varidx_code>/"
            p = p.replace("<varidx_code>", cntx.varidx.get_code())
            code_l = utils.list_dir(p)
        elif cntx.view.get_code() == view_def.mode_tbl:
            df = utils.load_data(cntx)
            code_l = list(dict.fromkeys(list(df["hor"])))
            code_l.remove(df[df["rcp"] == rcp_def.rcp_ref]["hor"][0])
        code_l.sort()

        # Remove the items that includes all years.
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

        # Create items.
        self.items = []
        for code in code_l:
            self.items.append(Hor(code))
            
    def add(
        self,
        code: Union[str, List[str]]
    ):
        
        """
        Add one or several items.
        
        Paramters
        ---------
        code : Union[str, List[str]]
            Code or list of codes.
        """        
        
        code_l = code
        if isinstance(code, str):
            code_l = [code]
        
        new = Hors()
        for i in range(len(code_l)):
            new.items.append(Hor(code_l[i]))
        
        return new
    
    def remove(
        self,
        code: Union[str, List[str]]
    ):
        
        """
        Remove one or several items.
        
        Paramters
        ---------
        code : Union[str, List[str]]
            Code or list of codes.
        """
        
        code_l = code
        if isinstance(code, str):
            code_l = [code]
        
        new = self.copy()
        for i in range(len(code_l)):
            for j in range(len(new.items)):
                if new.items[j].code == code:
                    del new.items[j]
                    break
        
        return new
    
    def copy(self):
        
        """
        Copy items.
        """
        
        new = Hors()
        for item in self.items:
            new.items.append(Hor(item.code))
        
        return new

    def get_code_l(
        self
    ) -> List[str]:

        """
        Get codes.

        Returns
        -------
        List[str]
            Codes.
        """

        code_l = []

        for item in self.items:
            code_l.append(item.get_code())

        return code_l
