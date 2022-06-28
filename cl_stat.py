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
from typing import List, Optional, Union

# Dashboard libraries.
import cl_gd
import cl_object
from cl_constant import const as c
from cl_context import cntx


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
        c.STAT_MEAN:           "Moyenne",
        c.STAT_STD:            "Écart type",
        c.STAT_MIN:            "Minimum",
        c.STAT_MAX:            "Maximum",
        c.STAT_SUM:            "Somme",
        c.STAT_MEDIAN:         "Médiane",
        c.STAT_QUANTILE:       "Quantile",
        c.STAT_CENTILE:        "Centile",
        c.STAT_CENTILE_LOWER:  str(centile) + "e" + ("r" if centile == 1 else "")  + " centile",
        c.STAT_CENTILE_MIDDLE: str(centile) + "e" + ("r" if centile == 1 else "")  + " centile",
        c.STAT_CENTILE_UPPER:  str(centile) + "e" + ("r" if centile == 1 else "")  + " centile"
    }


class Stat(
    cl_object.Obj
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

        desc = dict(code_desc(centile_act))[c.STAT_CENTILE_MIDDLE if centile_act >= 0 else self.code]

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

        return (self.code in [c.STAT_CENTILE, c.STAT_CENTILE_LOWER, c.STAT_CENTILE_MIDDLE, c.STAT_CENTILE_UPPER]) or\
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
        if self.code in [c.STAT_CENTILE, c.STAT_CENTILE_LOWER, c.STAT_CENTILE_MIDDLE, c.STAT_CENTILE_UPPER]:
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


class Stats(cl_object.Objs):

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
            is_ref = cntx.rcp.code == c.REF

        # Codes.
        project_code = cntx.project.code if cntx.project is not None else ""
        view_code  = cntx.view.code if cntx.view is not None else ""
        vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
        vi_name    = cntx.varidx.name if cntx.varidx is not None else ""
        rcp_code   = cntx.rcp.code if cntx.rcp is not None else ""
        hor_code   = cntx.hor.code if cntx.hor is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else "False"

        # The items are extracted from the configuration file.
        if view_code in [c.VIEW_TS, c.VIEW_TS_BIAS]:

            centile_l = cntx.opt_ts_centiles
            for i in range(len(centile_l)):
                code_l.append("c" + str(centile_l[i]).rjust(3, "0"))

        # The items are extracted from the configuration file.
        if view_code == c.VIEW_TBL:

            centile_l = cntx.opt_tbl_centiles
            for i in range(len(centile_l)):
                code_l.append("c" + str(centile_l[i]).rjust(3, "0"))

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*.csv"
        elif view_code == c.VIEW_MAP:

            pattern = project_code + "/<view_code>/<vi_code>/<hor_code>/<vi_name>_<rcp_code>_<hor_code_>_*.csv"
            pattern = pattern.replace("<view_code>", view_code)
            pattern = pattern.replace("<vi_code>", vi_code)
            pattern = pattern.replace("<vi_name>", vi_name)
            pattern = pattern.replace("<rcp_code>", rcp_code)
            pattern = pattern.replace("<hor_code_>", "" if cntx.hor is None else hor_code.replace("-", "_"))
            pattern = pattern.replace("<hor_code>", hor_code)

            p_l = list(cntx.files(pattern)[cl_gd.PROP_PATH])

            # Add each code for which a file exists.
            for p_i in p_l:

                # Skip if looking for files with absolute values.
                if ("delta" in p_i) and (delta_code == "False"):
                    continue

                # Extract statistic code.
                tokens = p_i.replace(c.F_EXT_CSV, "").replace("_delta", "").split("_")
                code = tokens[len(tokens) - 1]

                # Any statistic, except a centile.
                if "c" not in code:
                    if code not in code_l:
                        code_l.append(code)
                        centile_l.append(-1)

                # A centile.
                elif (not is_ref) or (is_ref and (code == c.STAT_MEAN)):
                    if code not in code_l:
                        code_l.append(code)
                        centile_l.append(int(code.replace("c", "")))

            # Only keep the mean if the reference period was selected.
            if (hor_code == cntx.per_ref_str) and (c.STAT_MEAN in code_l):
                code_l = [c.STAT_MEAN]
                centile_l = [-1]

        # The items are extracted from the configuration file.
        elif view_code == c.VIEW_CLUSTER:
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

        desc_l.sort()

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
