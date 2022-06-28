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
import pandas as pd
from typing import List, Union

# Dashboard libraries.
import cl_auth
import cl_gd
import cl_object
from cl_constant import const as c
from cl_context import cntx


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
        c.REF:   ["Référence", "black"],
        c.RCP26: ["RCP 2.6",   "blue"],
        c.RCP45: ["RCP 4.5",   "green"],
        c.RCP85: ["RCP 8.5",   "red"],
        c.RCPXX: ["Tous",      "pink"]
    }


class RCP(cl_object.Obj):

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

        return self.code == c.REF


class RCPs(cl_object.Objs):

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
        project_code = cntx.project.code if cntx.project is not None else ""
        view_code = cntx.view.code if cntx.view is not None else ""
        vi_code   = cntx.varidx.code if cntx.varidx is not None else ""
        vi_name   = cntx.varidx.name if cntx.varidx is not None else ""
        if view_code == c.VIEW_CLUSTER:
            view_code = c.VIEW_TS
            vi_code = cntx.varidxs.items[0].code
            vi_name = cntx.varidxs.items[0].name
        hor_code   = cntx.hor.code if cntx.hor is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else "False"

        # Base directory.
        p_base = str(cl_auth.path(project_code))

        # The items are extracted from the 'rcp' column of data files ('tbl' view).
        # ~/<project_code>/tbl/<vi_code>*.csv
        if view_code == c.VIEW_TBL:

            p = "<view_code>/<vi_code>/<vi_name>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<vi_name>", vi_name)

            if cntx.project.drive is not None:
                df = pd.DataFrame(cntx.project.drive.load_csv(path=p))
            else:
                df = pd.read_csv(p_base + "/" + project_code + "/" + p)

            item_l = list(df.columns) if view_code == c.VIEW_TS else df["rcp"]
            if (delta_code == "True") and (c.REF in item_l):
                item_l.remove(c.REF)

        # The items are extracted from column names ('ts' or 'ts_bias' view).
        # ~/<project_code>/<view_code>/<vi_code>/*.csv
        elif view_code in [c.VIEW_TS, c.VIEW_TS_BIAS]:

            p = "<view_code>/<vi_code>/<vi_name>_<mode>_<delta>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<vi_name>", vi_name)
            p = p.replace("<mode>", "rcp")
            p = p.replace("_<delta>", "_delta" if delta_code == "True" else "")

            if cntx.project.drive is not None:
                df = pd.DataFrame(cntx.project.drive.load_csv(path=p))
            else:
                df = pd.read_csv(p_base + "/" + project_code + "/" + p)

            item_l = list(df.columns)
            if c.REF in item_l:
                item_l.remove(c.REF)

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*
        elif view_code == c.VIEW_MAP:

            pattern = project_code + "/<view_code>/<vi_code>/<hor_code>/*.csv"
            pattern = pattern.replace("<view_code>", view_code)
            pattern = pattern.replace("<vi_code>", vi_code)
            pattern = pattern.replace("<hor_code>", hor_code)

            item_l = list(cntx.files(pattern)[cl_gd.PROP_PATH])

            # Only keep the reference dataset if the reference period was selected.
            if hor_code == cntx.per_ref_str:
                item_l_tmp = []
                for item in item_l:
                    if c.REF in item:
                        item_l_tmp.append(item)
                        break
                item_l = item_l_tmp

        # The items are extracted from file names.
        # ~/<project_code>/cycle*/<vi_code>/<hor_code>/*.csv
        elif view_code == c.VIEW_CYCLE:

            pattern = project_code + "/<view_code>*/<vi_code>/<hor_code>/*.csv"
            pattern = pattern.replace("<view_code>", view_code)
            pattern = pattern.replace("<vi_code>", vi_code)
            pattern = pattern.replace("<hor_code>", hor_code)

            item_l = list(cntx.files(pattern)[cl_gd.PROP_PATH])

        else:
            item_l = []

        # Extract RCPs.
        # Sort items, but let the reference emission scenario be first.
        code_l = []
        ref_found = False
        for item in item_l:
            code = ""
            if c.REF in item:
                ref_found = True
            elif c.RCP26 in item:
                code = c.RCP26
            elif c.RCP45 in item:
                code = c.RCP45
            elif c.RCP85 in item:
                code = c.RCP85
            if (code != "") and (code not in code_l):
                code_l.append(code)
        code_l.sort()
        if ref_found and (delta_code == "False"):
            code_l = [c.REF] + code_l

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

        if c.REF in code_l:
            code_l.remove(c.REF)
            code_l = [c.REF] + code_l

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

        if code_props()[c.REF][0] in desc_l:
            desc_l.remove(code_props()[c.REF][0])
            desc_l = [code_props()[c.REF][0]] + desc_l

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

        if code_props()[c.REF][1] in color_l:
            color_l.remove(code_props()[c.REF][1])
            color_l = [code_props()[c.REF][1]] + color_l

        return color_l
