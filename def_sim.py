# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Sim and Sims
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
import os
import pandas as pd
from typing import List, Union

# Dashboard libraries.
import def_object
import def_rcp
from def_constant import const as c
from def_context import cntx


def code_desc(
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
        c.simxx: "Toutes"
    }


class Sim(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Sim.
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

        desc = dict(code_desc())[code] if code == c.simxx else code
        super(Sim, self).__init__(code=code, desc=desc)

    @property
    def rcm(
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

        rcm = ""

        tokens = self.code.split("_")
        if len(tokens) >= 4:
            rcm = tokens[0]

        return rcm

    @property
    def domain(
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

        domain = ""

        tokens = self.code.split("_")
        if len(tokens) >= 4:
            domain = tokens[1]

        return domain

    @property
    def gcm(
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

        gcm = ""

        tokens = self.code.split("_")
        if len(tokens) >= 4:
            gcm = tokens[2]

        return gcm

    @property
    def rcp(
        self
    ) -> Union[def_rcp.RCP, None]:

        """
        ----------------------------------------
        Get RCP.

        Returns
        -------
        def_rcp.RCP
            RCP.
        ----------------------------------------
        """

        rcp = None

        if self.code == c.ref:
            rcp = def_rcp.RCP(c.ref)
        else:
            tokens = self.code.split("_")
            if len(tokens) >= 4:
                rcp = def_rcp.RCP(tokens[3])

        return rcp

    @property
    def desc(
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

        desc = self.code

        if self.code == c.ref:
            desc = self.rcp.desc
        else:
            tokens = self.code.split("_")
            if len(tokens) >= 4:
                desc = self.rcm + "_" + self.gcm + " (" + self.rcp.desc + ")"

        return desc


class Sims(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Sims.
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

        super(Sims, self).__init__()

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

        # Codes.
        view_code  = cntx.view.code if cntx.view is not None else ""
        if view_code == c.view_cluster:
            view_code = c.view_ts
        vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
        hor_code   = cntx.hor.code if cntx.hor is not None else ""
        rcp_code   = cntx.rcp.code if cntx.rcp is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else False

        # The items are extracted from file names.
        # ~/<project_code>/<view_code>*/<vi_code>/<hor_code>/*.csv
        if view_code == c.view_cycle:
            p = cntx.d_project + "<view_code>*/<vi_code>/<hor_code>/*<rcp_code>*.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<hor_code>", hor_code)
            p = p.replace("<rcp_code>", rcp_code)

            # The code of each simulation is set to <RCM>_<domain>_<GCM>_<RCP>.
            ref_found = False
            for p in list(glob.glob(p)):
                if c.ref in p:
                    ref_found = True
                else:
                    tokens = os.path.basename(p).split("_")
                    code = tokens[1] + "_" + tokens[2] + "_" + tokens[3] + "_" + tokens[4]
                    if code not in code_l:
                        code_l.append(code)
            if ref_found:
                code_l = [c.ref] + code_l

        # The items are extracted from columns.
        # ~/<project_code>/<view_code>/<vi_code>/<vi_code>_sim_*.csv
        elif view_code in [c.view_ts, c.view_ts_bias]:
            p = cntx.d_project + "<view_code>/<vi_code>/<vi_code>_sim_<delta>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("_<delta>", "_delta" if delta_code == "True" else "")
            df = pd.read_csv(p)
            df.drop(["year", c.ref], axis=1, inplace=True)
            for column in list(df.columns):
                if (rcp_code in ["", c.rcpxx]) or ((rcp_code not in ["", c.rcpxx]) and (rcp_code in column)):
                    code_l.append(column)

        # Sort list and put reference first.
        code_l.sort()

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], Sim],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[str, List[str], Sim]
            Item (code, list of codes or instance of Sim).
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, Sim):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(Sim(code_l[i]))

        return super(Sims, self).add(items, inplace)

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

        for item in self.items:
            desc_l.append(item.desc)

        return desc_l
