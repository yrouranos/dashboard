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

# Dashboard libraries.
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

    centile_lower_str, centile_upper_str = "10", "90"
    if cntx.project.stat is not None:
        if len(cntx.project.stats.centile_l) >= 2:
            centile_lower_str = cntx.project.stats.centile_as_str_l[0]
            centile_upper_str = cntx.project.stats.centile_as_str_l[len(cntx.project.stats.centile_as_str_l) - 1]

    return {
        c.stat_min:           "Minimum",
        c.stat_centile_lower: centile_lower_str + "e centile",
        c.stat_median:        "Médiane",
        c.stat_centile_upper: centile_upper_str + "e centile",
        c.stat_max:           "Maximum",
        c.stat_mean:          "Moyenne",
        c.stat_std:           "Écart type",
        c.stat_sum:           "Somme",
        c.stat_quantile:      "Quantile",
        c.stat_centile:       "Centile"
    }


class Stat(
    def_object.Obj
):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stat.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Centile (value between 0 and 100).
    _centile = -1.0

    def __init__(
        self,
        code: str,
        centile: Optional[float] = -1.0
    ):

        """
        ----------------------------------------
        Constructor.

        Parameters
        ----------
        code: str
            Code. See options in 'code_desc()'.
        centile: Optional[float]
            Centile (value between 0 and 100).
        ----------------------------------------
        """

        desc = "" if code == "" else dict(code_desc())[code]
        super(Stat, self).__init__(code=code, desc=desc)
        self.centile = centile

    @property
    def centile(
        self
    ) -> float:

        """
        ----------------------------------------
        Get centile.

        Returns
        -------
        float
            Centile (value between 0 and 100).
        ----------------------------------------
        """

        return self._centile

    @centile.setter
    def centile(
        self,
        centile: float
    ):

        """
        ----------------------------------------
        Set centile.

        Parameters
        ----------
        centile: float
            Centile (value between 0 and 100).
        ----------------------------------------
        """

        self._centile = centile

    @property
    def centile_as_str(
        self
    ) -> str:

        """
        ----------------------------------------
        Format centile.

        Returns
        -------
        str
            Formatted centile (between "c001" and "c100").
        ----------------------------------------
        """

        centile_as_str = "c" + str(int(self.centile)).rjust(3, "0")
        if "-" in centile_as_str:
            centile_as_str = ""

        return centile_as_str


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
            if isinstance(args[0], Stat):
                self.items = [args[0]]
            elif args[0] == "*":
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

    @property
    def centile_l(
        self
    ) -> List[float]:

        """
        ----------------------------------------
        Get centiles.

        Returns
        -------
        List[float]
            Centiles (values between 0 and 100).
        ----------------------------------------
        """

        centile_l = []
        for stat in self.items:
            centile_l.append(stat.centile)

        return centile_l

    @property
    def centile_as_str_l(
        self
    ) -> List[str]:

        """
        ----------------------------------------
        Format centiles.

        Returns
        -------
        List[str]
            Formatted centiles (between "c001" and "c100").
        ----------------------------------------
        """

        centile_as_str_l = []
        for stat in self.items:
            centile_as_str_l.append(stat.centile_as_str)

        return centile_as_str_l
