# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: RCP and RCPs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import config as cf
import glob
import object_def
import pandas as pd
import view_def
from typing import List, Union

# Reference period.
rcp_ref = "ref"

# Future period RCP 2.6.
rcp_26 = "rcp26"

# Future period RCP 4.5.
rcp_45 = "rcp45"

# Future period RCP 8.5.
rcp_85 = "rcp85"

# Any type of RCP.
rcp_xx = "rcpxx"

# Properties of emission scenarios.
code_props = {rcp_ref: ["Référence", "black"],
              rcp_26: ["RCP 2.6", "blue"],
              rcp_45: ["RCP 4.5", "green"],
              rcp_85: ["RCP 8.5", "red"],
              rcp_xx: ["Tous", "pink"]}


class RCP(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCP.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Contructor.
    def __init__(self, code):
        desc = "" if code == "" else code_props[code][0]
        super(RCP, self).__init__(code=code, desc=desc)
        self.color = "" if code == "" else code_props[self.code][1]
    
    def get_color(self) -> str:
        
        """
        Get color.
        
        Returns
        -------
        str
            Color.
        """
            
        return self.color


class RCPs(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCPs.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Constructors.
    def __init__(self, *args):
        super(RCPs, self).__init__()
    
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

        # The list of RCPs is within data files.
        if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
            p = cf.d_data + "<view>/<varidx_code>.csv"
            p = p.replace("<view>", cntx.view.get_code())
            p = p.replace("<varidx_code>", cntx.varidx.get_code())
            df = pd.read_csv(p)
            if cntx.view.get_code() == view_def.mode_ts:
                code_l = list(df.columns)
            else:
                code_l = df["rcp"]
            if cntx.delta and (rcp_ref in code_l):
                code_l.remove(rcp_ref)

        # The list of RCPs is within file structure.
        else:
            p = cf.d_data + "<view>/<varidx_code>/<hor>/*.csv"
            p = p.replace("<view>", cntx.view.get_code())
            p = p.replace("<varidx_code>", cntx.varidx.get_code())
            p = p.replace("<hor>", cntx.hor.get_code())
            code_l = list(glob.glob(p))

        # Extract RCPs.
        code_clean_l = []
        for code in code_l:
            if ("rcp" in code) or (rcp_ref in code):
                i_token = 0 if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl] else 1
                code = code.split("_")[i_token]
                if code not in code_clean_l:
                    code_clean_l.append(code)
        code_clean_l.sort()

        self.add(code_clean_l)

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
            items.append(RCP(code_l[i]))

        return super(RCPs, self).add_items(items, inplace)

    def get_code_l(self) -> List[str]:

        """
        Get a list of codes.

        Returns
        -------
        List[str]
            Codes.
        """

        code_l = super(RCPs, self).get_code_l()

        if rcp_ref in code_l:
            code_l.remove(rcp_ref)
            code_l = [rcp_ref] + code_l

        return code_l

    def get_desc_l(self) -> List[str]:

        """
        Get a list of descriptions.

        Returns
        -------
        List[str]
            Descriptions.
        """

        desc_l = super(RCPs, self).get_desc_l()

        if code_props[rcp_ref][0] in desc_l:
            desc_l.remove(code_props[rcp_ref][0])
            desc_l = [code_props[rcp_ref][0]] + desc_l

        return desc_l

    def get_color_l(
        self
    ) -> List[str]:
    
        """
        Get colors.
    
        Returns
        -------
        List[str]
            Colors.
        """
    
        color_l = []
        for item in self.items:
            color_l.append(item.get_color())

        if code_props[rcp_ref][1] in color_l:
            color_l.remove(code_props[rcp_ref][1])
            color_l = [code_props[rcp_ref][1]] + color_l

        return color_l
