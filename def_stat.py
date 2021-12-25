# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Stat and Stats.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import dash_utils
import def_context
import def_object
import def_rcp
import def_view
import os
from typing import List, Union
        
code_min      = "min"
code_q_low    = "q10"
code_median   = "median"
code_q_high   = "q90"
code_max      = "max"
code_mean     = "mean"
code_sum      = "sum"
code_quantile = "quantile"


def get_code_desc():

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and descriptions.

    Note that 'code_q_low' and 'code_q_high' vary with the context, in particular, project and variable.

    Returns
    -------
    dict
        Dictionary of codes and descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """

    return {
        code_min: "Minimum",
        code_q_low: code_q_low.replace("q", "") + "e percentile",
        code_median: "Médiane",
        code_q_high: code_q_high.replace("q", "") + "e percentile",
        code_max: "Maximum",
        code_mean: "Moyenne"
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

        desc = "" if code == "" else dict(get_code_desc())[code]
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
            if isinstance(args[0], str) or isinstance(args[0], list):
                self.add(args[0])
            else:
                self.load(args[0])

    def load(
        self,
        cntx: def_context.Context
    ):

        """
        ----------------------------------------
        Load items.
        
        Parameters
        ----------
        cntx : def_context.Context
            Context.
        ----------------------------------------
        """

        code_l = []

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*.csv"
        if cntx.view.get_code() == def_view.code_map:
            p = str(dash_utils.get_d_data(cntx)) +\
                "<view_code>/<vi_code>/<hor_code>/<vi_name>_<rcp_code>_<hor_code_>_<stat>_<delta>.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("<vi_name>", cntx.varidx.get_code())
            p = p.replace("<rcp_code>", "" if cntx.rcp is None else cntx.rcp.get_code())
            p = p.replace("<hor_code_>", "" if cntx.hor is None else cntx.hor.get_code().replace("-", "_"))
            p = p.replace("<hor_code>", "" if cntx.hor is None else cntx.hor.get_code())
            p = p.replace("_<delta>", "" if not cntx.delta.get_code() else "_delta")

            is_rcp_ref = cntx.rcp.get_code() == def_rcp.rcp_ref
            for code in list(get_code_desc().keys()):
                if os.path.exists(p.replace("<stat>", code)) and\
                   ((not is_rcp_ref) or (is_rcp_ref and (code == code_mean))):
                    code_l.append(code)

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
            items.append(Stat(code_l[i]))

        return super(Stats, self).add_items(items, inplace)
