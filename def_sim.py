# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Sim and Sims
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
import glob
import os
import pandas as pd
from typing import List, Union


class Sim(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Sim.
    --------------------------------------------------------------------------------------------------------------------
    """

    # RCM.
    rcm = ""

    # Domain.
    domain = ""

    # GCM.
    gcm = ""

    # RCP.
    rcp = None

    def __init__(
        self,
        code: str
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        desc = def_rcp.RCP(def_rcp.rcp_ref).get_desc() if code == def_rcp.rcp_ref else code
        super(Sim, self).__init__(code=code, desc=desc)

    def get_rcm(
        self
    ) -> str:

        """
        ----------------------------------------
        Get RCM.

        Returns
        -------
        str
            RCM.
        ----------------------------------------
        """

        return self.code.split("_")[0]

    def get_domain(
        self
    ) -> str:

        """
        ----------------------------------------
        Get domain.

        Returns
        -------
        str
            Domain.
        ----------------------------------------
        """

        return self.code.split("_")[1]

    def get_gcm(
        self
    ) -> str:

        """
        ----------------------------------------
        Get GCM.

        Returns
        -------
        str
            GCM.
        ----------------------------------------
        """

        return self.code.split("_")[2]

    def get_rcp(
        self
    ) -> def_rcp.RCP:

        """
        ----------------------------------------
        Get RCP.

        Returns
        -------
        def_rcp.RCP
            RCP.
        ----------------------------------------
        """

        return def_rcp.RCP(self.code.split("_")[3])

    def get_desc(
        self
    ) -> str:

        """
        ----------------------------------------
        Get description.

        Returns
        -------
        str
            Description.
        ----------------------------------------
        """

        return self.get_rcm() + "_" + self.get_gcm() + " (" + self.get_rcp().get_desc() + ")"


class Sims(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Sims.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Sims, self).__init__()

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
        rcp_ref_found = False

        # The items are extracted from file names.
        # ~/<project_code>/<view_code>*/<vi_code>/<hor_code>/*.csv
        if cntx.view.get_code() == def_view.code_cycle:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>*/<vi_code>/<hor_code>/*<rcp_code>*.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("<hor_code>", cntx.hor.get_code())
            p = p.replace("<rcp_code>", cntx.rcp.get_code())

            # The code of each simulation is set to <RCM>_<domain>_<GCM>_<RCP>.
            for p in list(glob.glob(p)):
                if def_rcp.rcp_ref in p:
                    rcp_ref_found = True
                else:
                    tokens = os.path.basename(p).split("_")
                    code = tokens[1] + "_" + tokens[2]+ "_" + tokens[3] + "_" + tokens[4]
                    if code not in code_l:
                        code_l.append(code)

        # The items are extracted from columns.
        # ~/<project_code>/<view_code>/<vi_code>/<vi_code>_sim_*.csv
        elif cntx.view.get_code() in [def_view.code_ts, def_view.code_bias]:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>/<vi_code>/<vi_code>_sim_<delta>.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<vi_code>", cntx.varidx.get_code())
            p = p.replace("_<delta>", "_delta" if cntx.delta.get_code() else "")
            df = pd.read_csv(p)
            columns = list(df.columns)
            for column in columns:
                if not cntx.delta.get_code() or (def_rcp.rcp_ref not in column):
                    code = ""
                    if def_rcp.rcp_ref in column:
                        rcp_ref_found = True
                    elif def_rcp.rcp_26 in column:
                        code = def_rcp.rcp_26
                    elif def_rcp.rcp_45 in column:
                        code = def_rcp.rcp_45
                    elif def_rcp.rcp_85 in column:
                        code = def_rcp.rcp_85
                    if (code != "") and (code not in code_l):
                        code_l.append(code)

        # Sort list and put reference first.
        code_l.sort()
        if rcp_ref_found:
            code_l = [def_rcp.rcp_ref] + code_l

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
            items.append(Sim(code_l[i]))

        return super(Sims, self).add_items(items, inplace)

    def get_code(
        self,
        desc: str
    ) -> str:

        """
        ----------------------------------------
        Get code.

        Paramters
        ---------
        desc : str
            Description.

        Returns
        -------
        str
            Code.
        ----------------------------------------
        """

        for item in self.items:
            if item.get_desc() == desc:
                return item.code

        return ""

    def get_desc_l(
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

        for item in self.items:
            desc_l.append(item.get_desc())

        return desc_l
