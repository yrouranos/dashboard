# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Class definition: Project and Projects.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
from typing import List, Union, Optional

# Dashboard libraries.
import dash_utils as du
import def_object
from def_constant import const as c
from def_context import cntx
from def_stat import Stat, Stats


class Project(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Project.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code: str = ""
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Project, self).__init__(code=code, desc=code)

        cntx.load()

        if code != "":
            self._stats = Stats()
            for _ in range(2):
                self._stats.add(Stat(c.stat_centile, -1))


class Projects(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Projects.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        code: Union[str, List[str]] = ""
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Projects, self).__init__()

        if code == "*":
            self.load()
        elif code != "":
            self.add(code)

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        code_l = du.list_dir(cntx.d_data)
        if isinstance(code_l, List):
            code_l.sort()

        self.add(code_l)

    def add(
        self,
        item: Union[str, List[str], Project],
        inplace: Optional[bool] = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Parameters
        ----------
        item: Union[str, List[str], Project]
            Item (code, list of codes or instance of Project).
        inplace: Optional[bool]
            If True, modifies the current instance.
        ----------------------------------------
        """

        items = []

        if isinstance(item, Project):
            items = [item]

        else:
            code_l = item
            if isinstance(item, str):
                code_l = [item]
            for i in range(len(code_l)):
                items.append(Project(code_l[i]))

        return super(Projects, self).add(items, inplace)
