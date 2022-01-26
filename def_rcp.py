# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: RCP and RCPs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
import pandas as pd
from typing import List, Union

# Dashboard libraries.
import def_object
from def_constant import const as c
from def_context import cntx


def code_props(
) -> dict:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and properties.

    Returns
    -------
    dict
        Dictionary of codes and properties.
    --------------------------------------------------------------------------------------------------------------------
    """

    return {
        c.ref:   ["Référence", "black"],
        c.rcp26: ["RCP 2.6",   "blue"],
        c.rcp45: ["RCP 4.5",   "green"],
        c.rcp85: ["RCP 8.5",   "red"],
        c.rcpxx: ["Tous",      "pink"]
    }


class RCP(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCP.
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

        if code in list(dict(code_props()).keys()):
            super(RCP, self).__init__(code=code, desc=dict(code_props())[code][0])

    @property
    def color(
        self
    ) -> str:
        
        """
        ----------------------------------------
        Get color.
        
        Returns
        -------
        str
            Color.
        ----------------------------------------
        """

        return "" if self.code == "" else dict(code_props())[self.code][1]

    @property
    def is_ref(
        self
    ) -> bool:

        """
        ----------------------------------------
        Determine if the instance is a reference RCP.

        Returns
        -------
        bool
            True if the instance is a reference RCP.
        ----------------------------------------
        """

        return self.code == c.ref


class RCPs(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCPs.
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

        super(RCPs, self).__init__()

        if len(args) == 1:
            if args[0] == "*":
                self.load()
            else:
                self.add(args[0])

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        # Codes.
        view_code  = cntx.view.code if cntx.view is not None else ""
        vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
        if view_code == c.view_cluster:
            view_code = c.view_ts
            vi_code = cntx.varidxs.items[0].code
        hor_code   = cntx.hor.code if cntx.hor is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else False

        # The items are extracted from the 'rcp' column of data files ('tbl' view).
        # ~/<project_code>/tbl/<vi_code>*.csv
        if view_code == c.view_tbl:
            p = cntx.d_project + "<view_code>/<vi_code>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            df = pd.read_csv(p)
            item_l = list(df.columns) if view_code == c.view_ts else df["rcp"]
            if (delta_code == "True") and (c.ref in item_l):
                item_l.remove(c.ref)

        # The items are extracted from column names ('ts' or 'ts_bias' view).
        # ~/<project_code>/<view_code>/<vi_code>/*.csv
        elif view_code in [c.view_ts, c.view_ts_bias]:
            p = cntx.d_project + "<view_code>/<vi_code>/<vi_code>_<mode>_<delta>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<mode>", "rcp")
            p = p.replace("_<delta>", "_delta" if delta_code == "True" else "")
            df = pd.read_csv(p)
            item_l = list(df.columns)
            item_l.remove(c.ref)

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*
        elif view_code == c.view_map:
            p = cntx.d_project + "<view_code>/<vi_code>/<hor_code>/*.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<hor_code>", hor_code)
            item_l = list(glob.glob(p))

            # Only keep the reference dataset if the reference period was selected.
            if hor_code == cntx.per_ref_str:
                item_l_tmp = []
                for item in item_l:
                    if c.ref in item:
                        item_l_tmp.append(item)
                        break
                item_l = item_l_tmp

        # The items are extracted from file names.
        # ~/<project_code>/cycle*/<vi_code>/<hor_code>/*.csv
        elif view_code == c.view_cycle:
            p = cntx.d_project + "<view_code>*/<vi_code>/<hor_code>/*.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<hor_code>", hor_code)
            item_l = glob.glob(p)

        else:
            item_l = []

        # Extract RCPs.
        # Sort items, but let the reference emission scenario be first.
        code_l = []
        ref_found = False
        for item in item_l:
            code = ""
            if c.ref in item:
                ref_found = True
            elif c.rcp26 in item:
                code = c.rcp26
            elif c.rcp45 in item:
                code = c.rcp45
            elif c.rcp85 in item:
                code = c.rcp85
            if (code != "") and (code not in code_l):
                code_l.append(code)
        code_l.sort()
        if ref_found and (delta_code == "False"):
            code_l = [c.ref] + code_l

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], RCP],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[str, List[str], RCP]
            Item (code, list of codes or instance of RCP).
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, RCP):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(RCP(code_l[i]))

        return super(RCPs, self).add(items, inplace)

    @property
    def code_l(
        self
    ) -> List[str]:

        """
        ----------------------------------------
        Get a list of codes.

        Returns
        -------
        List[str]
            Codes.
        ----------------------------------------
        """

        code_l = super(RCPs, self).code_l

        if c.ref in code_l:
            code_l.remove(c.ref)
            code_l = [c.ref] + code_l

        return code_l

    @property
    def desc_l(
        self
    ) -> List[str]:

        """
        ----------------------------------------
        Get a list of descriptions.

        Returns
        -------
        List[str]
            Descriptions.
        ----------------------------------------
        """

        desc_l = super(RCPs, self).desc_l

        if code_props()[c.ref][0] in desc_l:
            desc_l.remove(code_props()[c.ref][0])
            desc_l = [code_props()[c.ref][0]] + desc_l

        return desc_l

    @property
    def color_l(
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
            color_l.append(item.color)

        if code_props()[c.ref][1] in color_l:
            color_l.remove(code_props()[c.ref][1])
            color_l = [code_props()[c.ref][1]] + color_l

        return color_l
