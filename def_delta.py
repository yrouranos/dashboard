# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Del and Dels.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import dash_utils
import def_context
import def_object
import def_view
import glob
from typing import Union, List

code_true = True
code_false = False


class Del(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Del.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code: bool
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Del, self).__init__(code=str(code), desc=str(code))

    def get_code(
            self
    ) -> bool:

        """
        ----------------------------------------
        Get code.

        Returns
        -------
        bool
            Code.
        ----------------------------------------
        """

        return bool(super(Del, self).code)


class Dels(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Dels.
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

        super(Dels, self).__init__()

        if len(args) == 1:
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

        code_l = [code_false, code_false]

        # The items are extracted from file names ('ts' or 'bias' view).
        # ~/<project_code>/<view_code>/<vi_code>/*delta.csv
        if cntx.view.get_code() in [def_view.code_ts, def_view.code_bias]:

            p = str(dash_utils.get_d_data(cntx)) + "<view_code>/*/*delta.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p_l = list(glob.glob(p))
            if len(p_l) > 0:
                code_l = [code_false, code_true]

        # The items are always available ('tbl' view).
        elif cntx.view.get_code() == def_view.code_tbl:
            code_l = [code_false, code_true]

        # The items are extracted from file names ('map' view).
        elif cntx.view.get_code() == def_view.code_map:
            p = str(dash_utils.get_d_data(cntx)) + "<view_code>/*/<hor_code>/*delta.csv"
            p = p.replace("<view_code>", cntx.view.get_code())
            p = p.replace("<hor_code>", cntx.hor.get_code())
            p_l = list(glob.glob(p))
            if len(p_l) > 0:
                code_l = [code_false, code_true]

        self.add(code_l)

    def add(
        self,
        code: Union[bool, List[bool]],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        code : Union[bool, List[bool]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        code_l = code
        if isinstance(code, bool):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(Del(code_l[i]))

        return super(Dels, self).add_items(items, inplace)

    def get_code_l(
        self
    ) -> List[bool]:

        """
        ----------------------------------------
        Get a list of codes.

        Returns
        -------
        List[bool]
            Codes.
        ----------------------------------------
        """

        code_l = []

        for item in self.items:
            code_l.append(bool(item.get_code()))

        return code_l
