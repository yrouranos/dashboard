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
from typing import List, Optional, Union

# Dashbaord libraries.
import def_object
from def_constant import const as c
from def_context import cntx


def code_desc(
) -> dict:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and descriptions.

    Returns
    -------
    dict
        Dictionary of codes and descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """

    project_code = cntx.project.code if cntx.project is not None else ""
    q_low_str  = "10"
    q_high_str = "90"
    if project_code != "":
        q_low_str  = cntx.project.quantiles_as_str[0]
        q_high_str = cntx.project.quantiles_as_str[len(cntx.project.quantiles_as_str) - 1]

    return {
        c.stat_min:      "Minimum",
        c.stat_q_low:    q_low_str + "e percentile",
        c.stat_median:   "Médiane",
        c.stat_q_high:   q_high_str + "e percentile",
        c.stat_max:      "Maximum",
        c.stat_mean:     "Moyenne",
        c.stat_sum:      "Somme",
        c.stat_quantile: "Quantile"
    }


class Stat(
    def_object.Obj
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stat.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Quantile (value between 0 and 1).
    _quantile = -1.0

    def __init__(
        self,
        code: str,
        quantile: Optional[float] = -1.0
    ):

        """
        ----------------------------------------
        Constructor.

        Parameters
        ----------
        code: str
            Code. See options in 'code_desc()'.
        quantile: Optional[float]
            Quantile (value between 0 and 1).
        ----------------------------------------
        """

        desc = "" if code == "" else dict(code_desc())[code]
        super(Stat, self).__init__(code=code, desc=desc)
        self.quantile = quantile

    @property
    def quantile(
        self
    ) -> float:

        """
        ----------------------------------------
        Get quantile.

        Returns
        -------
        float
            Quantile (value between 0 and 1).
        ----------------------------------------
        """

        return self._quantile

    @quantile.setter
    def quantile(
        self,
        quantile: float
    ):

        """
        ----------------------------------------
        Set quantile.

        Parameters
        ----------
        quantile: float
            Quantile (value between 0 and 1).
        ----------------------------------------
        """

        self._quantile = quantile


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
