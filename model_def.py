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

import glob
import object_def
import rcp_def
import utils
from typing import List, Union


class Model(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Model.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, code):

        """
        ----------------------------------------
        Contructor.
        ----------------------------------------
        """

        desc = rcp_def.RCP(rcp_def.rcp_ref).get_desc() if code == rcp_def.rcp_ref else code
        super(Model, self).__init__(code=code, desc=desc)


class Models(object_def.Objs):

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
            args[0] = cntx : context_def.Context
                Context.
        ----------------------------------------
        """

        cntx = args[0]

        # The items are extracted from file names.
        # ~/<project_code>/<view_code>*/<varidx_code>/<hor_code>/*.csv
        # The result only makes sense in the context of the 'disp' view.
        p = utils.get_d_data(cntx) + "<view_code>*/<varidx_code>/<hor_code>/*<rcp_code>*.csv"
        p = p.replace("<view_code>", cntx.view.get_code())
        p = p.replace("<varidx_code>", cntx.varidx.get_code())
        p = p.replace("<hor_code>", cntx.hor.get_code())
        p = p.replace("<rcp_code>", cntx.rcp.get_code())

        # The code of each model is set to <RCM>_<GCM>.
        code_l = []
        rcp_ref_found = False
        for p in list(glob.glob(p)):
            if rcp_def.rcp_ref in p:
                rcp_ref_found = True
            else:
                tokens = p.split("_")
                code = tokens[1] + "_" + tokens[2] + "_" + tokens[3]
                if code not in code_l:
                    code_l.append(code)
        code_l.sort()
        if rcp_ref_found:
            code_l = [rcp_def.rcp_ref] + code_l

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
