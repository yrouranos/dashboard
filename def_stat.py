# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Stat and Stats.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import os
from typing import List, Union

# Dashbaord libraries.
import def_object
from def_constant import const as c
from def_context import cntx


def code_desc(
) -> dict:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and descriptions.

    Note that 'code_q_low' and 'code_q_high' vary with the context (project and variable).

    Returns
    -------
    dict
        Dictionary of codes and descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """

    return {
        c.stat_min:    "Minimum",
        c.stat_q_low:  c.stat_q_low.replace("q", "") + "e percentile",
        c.stat_median: "Médiane",
        c.stat_q_high: c.stat_q_high.replace("q", "") + "e percentile",
        c.stat_max:    "Maximum",
        c.stat_mean:   "Moyenne"
    }


class Stat(
    def_object.Obj
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stat.
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

        desc = "" if code == "" else dict(code_desc())[code]
        super(Stat, self).__init__(code=code, desc=desc)


class Stats(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stats.
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

        super(Stats, self).__init__()

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

        code_l = []

        # Determine if this is the reference data.
        is_ref = False
        if cntx.rcp is not None:
            is_ref = cntx.rcp.code == c.ref

        # Codes.
        view_code  = cntx.view.code if cntx.view is not None else ""
        vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
        vi_name    = cntx.varidx.name if cntx.varidx is not None else ""
        rcp_code   = cntx.rcp.code if cntx.rcp is not None else ""
        hor_code   = cntx.hor.code if cntx.hor is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else False

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*.csv"
        if view_code == c.view_map:
            p = cntx.d_project + "<view_code>/<vi_code>/<hor_code>/<vi_name>_<rcp_code>_<hor_code_>_<stat>_<delta>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<vi_name>", vi_name)
            p = p.replace("<rcp_code>", rcp_code)
            p = p.replace("<hor_code_>", "" if cntx.hor is None else hor_code.replace("-", "_"))
            p = p.replace("<hor_code>", hor_code)
            p = p.replace("_<delta>", "" if delta_code == "False" else "_delta")

            # Add each code for which a file exists.
            for code in list(dict(code_desc()).keys()):
                if os.path.exists(p.replace("<stat>", code)) and ((not is_ref) or (is_ref and (code == c.stat_mean))):
                    code_l.append(code)

            # Only keep the mean if the reference period was selected.
            if hor_code == cntx.per_ref_str:
                code_l = [c.stat_mean] if (c.stat_mean in code_l) else []

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], Stat],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[str, List[str], Stat]
            Item (code, list of codes or instance of Stat).
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, Stat):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(Stat(code_l[i]))

        return super(Stats, self).add(items, inplace)
