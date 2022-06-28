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
import os
import pandas as pd
from typing import List, Union

# Dashboard libraries.
import cl_auth
import cl_gd
import cl_object
from cl_constant import const as c
from cl_context import cntx
from cl_rcp import RCP


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
        c.SIMXX: "Toutes"
    }


class Sim(cl_object.Obj):

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

        desc = dict(code_desc())[code] if code == c.SIMXX else code
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
    ) -> Union[RCP, None]:

        """
        ----------------------------------------
        Get RCP.

        Returns
        -------
        cl_rcp.RCP
            RCP.
        ----------------------------------------
        """

        rcp = None

        if self.code == c.REF:
            rcp = RCP(c.REF)
        else:
            tokens = self.code.split("_")
            if len(tokens) >= 4:
                rcp = RCP(tokens[3])

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

        if self.code == c.REF:
            desc = self.rcp.desc
        else:
            tokens = self.code.split("_")
            if len(tokens) >= 4:
                desc = self.rcm + "_" + self.gcm + " (" + self.rcp.desc + ")"

        return desc


class Sims(cl_object.Objs):

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
        project_code = cntx.project.code if cntx.project is not None else ""
        view_code  = cntx.view.code if cntx.view is not None else ""
        if view_code == c.VIEW_CLUSTER:
            view_code = c.VIEW_TS
        vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
        vi_name    = cntx.varidx.name if cntx.varidx is not None else ""
        hor_code   = cntx.hor.code if cntx.hor is not None else ""
        rcp_code   = cntx.rcp.code if cntx.rcp is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else "False"

        # Base directory.
        p_base = str(cl_auth.path(project_code))

        # The items are extracted from file names.
        # ~/<project_code>/<view_code>*/<vi_code>/<hor_code>/*.csv
        if view_code == c.VIEW_CYCLE:

            pattern = project_code + "/<view_code>*/<vi_code>/<hor_code>/*<rcp_code>*.csv"
            pattern = pattern.replace("<view_code>", view_code)
            pattern = pattern.replace("<vi_code>", vi_code)
            pattern = pattern.replace("<hor_code>", hor_code)
            pattern = pattern.replace("<rcp_code>", rcp_code)

            p_l = list(cntx.files(pattern)[cl_gd.PROP_PATH])

            # The code of each simulation is set to <RCM>_<domain>_<GCM>_<RCP>.
            ref_found = False
            for p_i in p_l:
                if c.REF in p_i:
                    ref_found = True
                else:
                    tokens = os.path.basename(p_i).split("_")
                    code = tokens[1] + "_" + tokens[2] + "_" + tokens[3] + "_" + tokens[4]
                    if code not in code_l:
                        code_l.append(code)
            if ref_found:
                code_l = [c.REF] + code_l

        # The items are extracted from columns.
        # ~/<project_code>/<view_code>/<vi_code>/<vi_code>_sim_*.csv
        elif view_code in [c.VIEW_TS, c.VIEW_TS_BIAS]:

            p = "<view_code>/<vi_code>/<vi_name>_sim_<delta>.csv"
            p = p.replace("<view_code>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("<vi_name>", vi_name)
            p = p.replace("_<delta>", "_delta" if delta_code == "True" else "")

            # Load CSV file.
            df = None
            if "gd:" in p_base:
                df = pd.DataFrame(cntx.project.drive.load_csv(path=p))
            else:
                p = p_base + "/" + project_code + "/" + p
                if os.path.exists(p):
                    df = pd.read_csv(p)

            if (df is not None) and (len(df) > 0):
                df.drop(["year", c.REF], axis=1, inplace=True)
                for column in list(df.columns):
                    if (rcp_code in ["", c.RCPXX]) or ((rcp_code not in ["", c.RCPXX]) and (rcp_code in column)):
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
