# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Project and Projects.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import context_def
import math
import object_def
from typing import List, Union

code_props = {"sn": ["sn", [0.1, 0.9]]}


class Project(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Project.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, code):

        """
        Contructor.
        """

        desc = "" if code == "" else code_props[code][0]
        super(Project, self).__init__(code=code, desc=desc)
        self.quantiles = [-1, -1] if code == "" else code_props[code][1]

    def get_quantiles(self) -> List[int]:

        """
        Get quantiles (low and high).

        Returns
        -------
        List[int]
            Quantiles.
        """

        return self.quantiles

    def get_quantiles_as_str(self) -> List[str]:

        """
        Get quantiles as string (low and high).

        Returns
        -------
        List[str]
            Formatted quantiles.
        """

        q_low = str(math.ceil(self.get_quantiles()[0] * 100))
        q_high = str(math.ceil(self.get_quantiles()[1] * 100))

        return [q_low, q_high]


class Projects(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Projects.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Constructors.
    def __init__(self, *args):
        super(Projects, self).__init__()

        if len(args) > 0:
            if isinstance(args[0], context_def.Context):
                self.load(args)
            else:
                self.add(args[0])

    def load(self, args):

        """
        Load items.

        Parameters
        ----------
        args :
            args[0] : cntx: context_def.Context
                Context.
        """

        cntx = args[0]

        code_l = []
        for code in list(code_props.keys()):
            code_l.append(code)

        self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        Add one or several items.

        Parameters
        ----------
        code : Union[str, List[str]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(Project(code_l[i]))

        return super(Projects, self).add_items(items, inplace)
