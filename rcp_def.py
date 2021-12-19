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

import glob
import object_def
import pandas as pd
import dash_utils
import view_def
from typing import List, Union

# Emission scenarios.
# The last item means all RCPs.
rcp_ref = "ref"
rcp_26  = "rcp26"
rcp_45  = "rcp45"
rcp_85  = "rcp85"
rcp_xx  = "rcpxx"

# Properties of emission scenarios.
code_props = {
    rcp_ref: ["Référence", "black"],
    rcp_26:  ["RCP 2.6", "blue"],
    rcp_45:  ["RCP 4.5", "green"],
    rcp_85:  ["RCP 8.5", "red"],
    rcp_xx:  ["Tous", "pink"]
}


class RCP(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCP.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    def __init__(self, code):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        desc = "" if code == "" else code_props[code][0]
        super(RCP, self).__init__(code=code, desc=desc)
        self.color = "" if code == "" else code_props[self.code][1]
    
    def get_color(self) -> str:
        
        """
        ----------------------------------------
        Get color.
        
        Returns
        -------
        str
            Color.
        ----------------------------------------
        """
            
        return self.color


class RCPs(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCPs.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(RCPs, self).__init__()

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
            args[0] = cntx : context_def.Context
                Context.
        ----------------------------------------
        """

        cntx = args[0]

        # The items are extracted from column names of data files ('ts' view).
        # ~/<project_code>/ts/<vi_code>/*.csv
        # The items are extracted from the 'rcp' column of data files ('tbl' view).
        # ~/<project_code>/tbl/<vi_code>/*.csv
        if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
            p = str(dash_utils.get_d_data(cntx)) + "/<view_code>/<vi_code>_<mode>.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("_<mode>", "_rcp" if cntx.view.get_code() == view_def.mode_ts else "")
            df = pd.read_csv(p)
            if cntx.view.get_code() == view_def.mode_ts:
                item_l = list(df.columns)
            else:
                item_l = df["rcp"]
            if cntx.delta and (rcp_ref in item_l):
                item_l.remove(rcp_ref)

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*
        elif cntx.view.get_code() == view_def.mode_map:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>/<vi_code>/<hor_code>/*.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("<hor_code>", cntx.hor.get_code())
            item_l = list(glob.glob(p))

        # The items are extracted from file names.
        # ~/<project_code>/cycle*/<vi_code>/<hor_code>/*.csv
        elif cntx.view.get_code() == view_def.mode_cycle:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>*/<vi_code>/<hor_code>/*.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("<hor_code>", cntx.hor.get_code())
            item_l = glob.glob(p)

        else:
            item_l = []

        # Extract RCPs.
        # Sort items, but let the reference emission scenario be first.
        code_l = []
        rcp_ref_found = False
        for item in item_l:
            code = ""
            if "rcp" not in item:
                rcp_ref_found = True
            elif rcp_26 in item:
                code = rcp_26
            elif rcp_45 in item:
                code = rcp_45
            elif rcp_85 in item:
                code = rcp_85
            if (code != "") and (code not in code_l):
                code_l.append(code)
        code_l.sort()
        if rcp_ref_found and not cntx.delta:
            code_l = [rcp_ref] + code_l

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
            items.append(RCP(code_l[i]))

        return super(RCPs, self).add_items(items, inplace)

    def get_code_l(self) -> List[str]:

        """
        ----------------------------------------
        Get a list of codes.

        Returns
        -------
        List[str]
            Codes.
        ----------------------------------------
        """

        code_l = super(RCPs, self).get_code_l()

        if rcp_ref in code_l:
            code_l.remove(rcp_ref)
            code_l = [rcp_ref] + code_l

        return code_l

    def get_desc_l(self) -> List[str]:

        """
        ----------------------------------------
        Get a list of descriptions.

        Returns
        -------
        List[str]
            Descriptions.
        ----------------------------------------
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
        ----------------------------------------
        Get colors.
    
        Returns
        -------
        List[str]
            Colors.
        ----------------------------------------
        """
    
        color_l = []
        for item in self.items:
            color_l.append(item.get_color())

        if code_props[rcp_ref][1] in color_l:
            color_l.remove(code_props[rcp_ref][1])
            color_l = [code_props[rcp_ref][1]] + color_l

        return color_l
