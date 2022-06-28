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
import cl_auth
import cl_gd
import cl_object
from cl_constant import const as c
from cl_context import cntx
from cl_stat import Stat, Stats


class Project(cl_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Project.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Path of .geogjson file defining region boundaries.
    _p_bounds = c.F_BOUNDS

    # Directory holding data (on local ore remote drive).
    _d_data = ""

    # Cloud drive.
    drive = None

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

        # Read project-specific configuration file.
        if cntx.code == c.PLATFORM_SCRIPT:
            cntx.load()

        if code != "":

            # Add statistics.
            self._stats = Stats()
            for _ in range(2):
                self._stats.add(Stat(c.STAT_CENTILE, -1))

            # Initialize cloud service.
            self._d_data = str(cl_auth.path(code))

            if "gd:" in self._d_data:
                self._d_data = self._d_data.replace("gd:", "")
                self.drive = cl_gd.GoogleDrive(self._d_data)
            else:
                self._d_data = c.D_DATA

    @property
    def d_data(
        self
    ) -> str:

        """
        ----------------------------------------
        Get the base directory of project.

        Returns
        -------
        str
            Local drive: Base directory of project.
            Cloud drive: Directory ID.
        ----------------------------------------
        """

        return self._d_data

    @property
    def p_bounds(
        self
    ) -> str:

        """
        ----------------------------------------
        Get the path of the .geojson file defining region boundaries.

        Returns
        -------
        str
            Local drive: Path of the .geojson file defining region boundaries.
            Cloud drive: File ID.
        ----------------------------------------
        """

        p = ""

        # Codes.
        project_code = cntx.project.code if cntx.project is not None else ""

        # Base directory.
        p_base = str(cl_auth.path(project_code))

        if cntx.code in [c.PLATFORM_STREAMLIT, c.PLATFORM_JUPYTER]:
            if self.drive is None:
                p = p_base + "/" + project_code + "/<view_code>/" + self._p_bounds
                p = p.replace("<view_code>", cntx.view.code)
            else:
                p_l = list(cntx.files(project_code + "/" + cntx.view.code + "/" + self._p_bounds)[cl_gd.PROP_ITEM_ID])
                if len(p_l) > 0:
                    p = p_l[0]
        else:
            p = self._p_bounds

        return p

    @p_bounds.setter
    def p_bounds(
        self,
        p_bounds: str
    ):

        """
        ----------------------------------------
        Set the path of the .geojson file defining region boundaries.

        Parameters
        ----------
        p_bounds: str
            Path of the .geojson file defining region boundaries.
        ----------------------------------------
        """

        self._p_bounds = p_bounds


class Projects(cl_object.Objs):

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
        Load items (all possibilities).
        ----------------------------------------
        """

        # List projects.
        code_l = str(cl_auth.Auth.projects)
        if ";" in code_l:
            code_l = code_l.split(";")

        if "context" in code_l:
            code_l.remove("context")

        # Sort.
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
