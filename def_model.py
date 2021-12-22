# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Model and models
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import dash_utils
import def_object
import def_rcp
import glob
import os
from typing import List, Union


class Model(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Model.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, code):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        desc = def_rcp.RCP(def_rcp.rcp_ref).get_desc() if code == def_rcp.rcp_ref else code
        super(Model, self).__init__(code=code, desc=desc)


class Models(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Models.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, *args):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Models, self).__init__()

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
            args[0] = cntx : def_context.Context
                Context.
        ----------------------------------------
        """

        cntx = args[0]

        # The items are extracted from file names.
        # ~/<project_code>/<view_code>*/<vi_code>/<hor_code>/*.csv
        # The result only makes sense in the context of the 'cycle' view.
        p = str(dash_utils.get_d_data(cntx)) + "<view_code>*/<vi_code>/<hor_code>/*<rcp_code>*.csv"
        p = p.replace("<view_code>", cntx.view.get_code())
        p = p.replace("<vi_code>", cntx.varidx.get_code())
        p = p.replace("<hor_code>", cntx.hor.get_code())
        p = p.replace("<rcp_code>", cntx.rcp.get_code())

        # The code of each model is set to <RCM>_<GCM>.
        code_l = []
        rcp_ref_found = False
        for p in list(glob.glob(p)):
            if def_rcp.rcp_ref in p:
                rcp_ref_found = True
            else:
                tokens = os.path.basename(p).split("_")
                code = tokens[1] + "_" + tokens[2] + "_" + tokens[3]
                if code not in code_l:
                    code_l.append(code)
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
            items.append(Model(code_l[i]))

        return super(Models, self).add_items(items, inplace)
