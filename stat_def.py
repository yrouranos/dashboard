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

import object_def
import os
import rcp_def
import dash_utils
import view_def
from typing import List, Union
        
mode_min = "min"
mode_q_low = "q10"
mode_median = "median"
mode_q_high = "q90"
mode_mean = "mean"
mode_max = "max"


def get_code_desc():

    """
    --------------------------------------------------------------------------------------------------------------------
    Get a dictionary of codes and descriptions.

    Note that 'mode_q_low' and 'mode_q_high' vary with the context, in particular, project and variable.

    Returns
    -------
    dict
        Dictionary of codes and descriptions.
    --------------------------------------------------------------------------------------------------------------------
    """

    return {
        mode_min: "Minimum",
        mode_q_low: mode_q_low.replace("q", "") + "e percentile",
        mode_median: "Médiane",
        mode_q_high: mode_q_high.replace("q", "") + "e percentile",
        mode_max: "Maximum",
        mode_mean: "Moyenne"
    }


class Stat(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stat.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, code):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        desc = "" if code == "" else get_code_desc()[code]
        super(Stat, self).__init__(code=code, desc=desc)


class Stats(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stats.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

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

        code_l = []

        # The items are extracted from file names.
        # ~/<project_code>/map/<vi_code>/<hor_code>/*.csv"
        if cntx.view.get_code() == view_def.mode_map:
            p = dash_utils.get_d_data(cntx) +\
                "<view_code>/<vi_code>/<hor_code>/<vi_name>_<rcp_code>_<hor_code_>_<stat>_<delta>.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("<vi_name>", cntx.varidx.get_code())
            p = p.replace("<rcp_code>", "" if cntx.rcp is None else cntx.rcp.get_code())
            p = p.replace("<hor_code_>", "" if cntx.hor is None else cntx.hor.get_code().replace("-", "_"))
            p = p.replace("<hor_code>", "" if cntx.hor is None else cntx.hor.get_code())
            p = p.replace("_<delta>", "" if cntx.delta is False else "_delta")

            is_rcp_ref = cntx.rcp.get_code() == rcp_def.rcp_ref
            for code in list(get_code_desc().keys()):
                if os.path.exists(p.replace("<stat>", code)) and\
                   ((not is_rcp_ref) or (is_rcp_ref and (code == mode_mean))):
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
