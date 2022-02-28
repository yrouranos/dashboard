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
import glob
import pandas as pd
from typing import List, Optional, Union

# Dashboard libraries.
import dash_utils as du
import def_object
from def_constant import const as c
from def_context import cntx


def code_desc(
    centile: Optional[int] = -1
) -> dict:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and descriptions.

    Parameters
    ----------
    centile: Optional[int]
        Centile.

    Returns
    -------
    dict
        Dictionary of codes and descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """

    return {
        c.stat_mean:           "Moyenne",
        c.stat_std:            "Écart type",
        c.stat_min:            "Minimum",
        c.stat_max:            "Maximum",
        c.stat_sum:            "Somme",
        c.stat_median:         "Médiane",
        c.stat_quantile:       "Quantile",
        c.stat_centile:        "Centile",
        c.stat_centile_lower:  str(centile) + "e centile",
        c.stat_centile_middle: str(centile) + "e centile",
        c.stat_centile_upper:  str(centile) + "e centile"
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
    _centile: int = -1

    def __init__(
        self,
        code: str,
        centile: Optional[int] = -1
    ):

        """
        ----------------------------------------
        Constructor.

        Examples
        --------
        code='mean'
        code='mean',    centile=-1
        code='centile', centile=10
        code='c010',    centile=10

        Parameters
        ----------
        code: str
            Code. See options in 'code_desc()'.
        centile: Optional[int]
            Centile (value between 0 and 100).
        ----------------------------------------
        """

        # Try to extract centile from code, then assign them to the instance.
        if ("c" in code) and (len(code) == 4) and (centile < 0):
            centile = round(int(code.replace("c", "")))

        self.code = code
        self.centile = centile

        super(Stat, self).__init__(code=code, desc=self.desc)

    @property
    def desc(
        self
    ) -> str:

        """
        ----------------------------------------
        Get description.

        Examples
        --------
        code='mean',    centile=-1 => 'Moyenne'
        code='centile', centile=10 => '10e centile'
        code='c010',    centile=10 => '10e centile'

        Returns
        -------
        str
            Description.
        ----------------------------------------
        """

        # Determine the actual centile (embedded in 'code' or in 'centile').
        centile_act = self.centile

        desc = dict(code_desc(centile_act))[c.stat_centile_middle if centile_act >= 0 else self.code]

        return desc

    @property
    def is_centile(
        self
    ) -> bool:

        """
        ----------------------------------------
        Determine whether this statistic is a centile.

        Examples
        --------
        code='mean',    centile=-1 => False
        code='centile', centile=10 => True
        code='c010',    centile=10 => True

        Returns
        -------
        bool
            True if this statistic is a centile.
        ----------------------------------------
        """

        return (self.code in [c.stat_centile, c.stat_centile_lower, c.stat_centile_middle, c.stat_centile_upper]) or\
               (("c" in self.code) and (len(self.code) == 4)) or (self.centile >= 0)

    @property
    def centile(
        self
    ) -> int:

        """
        ----------------------------------------
        Get centile.

        Examples
        --------
        code='mean',    centile=-1 => -1
        code='centile', centile=10 => 10
        code='c010',    centile=10 => 10

        Returns
        -------
        int
            Centile (value between 0 and 100).
        ----------------------------------------
        """

        centile_act = -1
        if self.code in [c.stat_centile, c.stat_centile_lower, c.stat_centile_middle, c.stat_centile_upper]:
            centile_act = self._centile
        elif ("c" in self.code) and (len(self.code) == 4):
            centile_act = int(self.code.replace("c", ""))

        return centile_act

    @centile.setter
    def centile(
        self,
        centile: int
    ):

        """
        ----------------------------------------
        Set centile.

        Parameters
        ----------
        centile: int
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
        Get centile as a string.

        Examples
        --------
        code='mean',    centile=-1 => ''
        code='centile', centile=10 => c010
        code='c010',    centile=10 => c010

        Returns
        -------
        str
            Centile as a string (between "c001" and "c100").
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
        centile_l = []

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

        # The items are extracted from the configuration file.
        if view_code in [c.view_ts, c.view_ts_bias]:
            centile_l = cntx.opt_ts_centiles
            for i in range(len(centile_l)):
                code_l.append("c" + str(centile_l[i]).rjust(3, "0"))

        # The items are extracted from the configuration file.
        if view_code == c.view_tbl:
            centile_l = cntx.opt_tbl_centiles
            for i in range(len(centile_l)):
                code_l.append("c" + str(centile_l[i]).rjust(3, "0"))

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*.csv"
        elif view_code == c.view_map:
            p = cntx.d_project + "<view_code>/<vi_code>/<hor_code>/<vi_name>_<rcp_code>_<hor_code_>_*.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<vi_name>", vi_name)
            p = p.replace("<rcp_code>", rcp_code)
            p = p.replace("<hor_code_>", "" if cntx.hor is None else hor_code.replace("-", "_"))
            p = p.replace("<hor_code>", hor_code)

            # Add each code for which a file exists.
            for p_i in list(glob.glob(p)):

                # Skip if looking for files with absolute values.
                if ("delta" in p_i) and (delta_code == "False"):
                    continue

                # Extract statistic code.
                tokens = p_i.replace(c.f_ext_csv, "").replace("_delta", "").split("_")
                code = tokens[len(tokens) - 1]

                # Any statistic, except a centile.
                if "c" not in code:
                    if code not in code_l:
                        code_l.append(code)
                        centile_l.append(-1)

                # A centile.
                elif (not is_ref) or (is_ref and (code == c.stat_mean)):
                    if code not in code_l:
                        code_l.append(code)
                        centile_l.append(int(code.replace("c", "")))

            # Only keep the mean if the reference period was selected.
            if (hor_code == cntx.per_ref_str) and (c.stat_mean in code_l):
                code_l = [c.stat_mean]
                centile_l = [-1]

        # The items are extracted from the configuration file.
        elif view_code == c.view_cluster:
            centile_l = cntx.opt_cluster_centiles
            for i in range(len(centile_l)):
                code_l.append("c" + str(centile_l[i]).rjust(3, "0"))

        # Add statistics.
        for i in range(len(code_l)):
            self.add(Stat(code_l[i], centile_l[i]))

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

        desc_l = []

        for item in self._items:
            desc_l.append(item.desc)

        return desc_l

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
