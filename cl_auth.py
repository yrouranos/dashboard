# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Streamlit entry point (authentication).
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import streamlit as st

# Session variables.
KEY_AUTH     = "auth"
KEY_USR      = "usr"
KEY_PWD      = "pwd"
KEY_PWD_OK   = "pwd_ok"
KEY_PROJECTS = "projects"
KEY_PROJECT  = "project"
KEY_PATH     = "path"

# Authentication instance.
auth = None


class Auth:

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Auth.
    --------------------------------------------------------------------------------------------------------------------
    """

    # User name.
    _usr = ""

    # Password.
    _pwd = ""

    # Projects.
    _projects = ""

    @property
    def usr(
        self
    ) -> str:

        """
        ----------------------------------------
        Get username.

        Returns
        -------
        str
            Username.
        ----------------------------------------
        """

        return self._usr

    @usr.setter
    def usr(
        self,
        usr: str
    ):

        """
        ----------------------------------------
        Set username.

        Parameters
        ----------
        usr: str
            Username.
        ----------------------------------------
        """

        self._usr = usr

    @property
    def pwd(
        self
    ) -> str:

        """
        ----------------------------------------
        Get password.

        Returns
        -------
        str
            Password.
        ----------------------------------------
        """

        return self._pwd

    @pwd.setter
    def pwd(
        self,
        pwd: str
    ):

        """
        ----------------------------------------
        Set password.

        Parameters
        ----------
        pwd: str
            Password.
        ----------------------------------------
        """

        self._pwd = pwd

    @property
    def validate_usr(
        self
    ) -> bool:

        """
        ----------------------------------------
        Verify if a user exists.

        Returns
        -------
        bool
            True if the user exists.
        ----------------------------------------
        """

        creds = st.secrets.credentials
        for cred in creds:
            if cred[KEY_USR] == self.usr:
                return True

        return False

    @property
    def validate_usr_pwd(
        self
    ) -> bool:

        """
        ----------------------------------------
        Validate access (user name and password).

        Returns
        -------
        bool
            True if the password is correct.
        ----------------------------------------
        """

        creds = st.secrets.credentials
        for cred in creds:
            if (cred[KEY_USR] == self.usr) and (cred[KEY_PWD] == self.pwd):
                return True

        return False

    @property
    def projects(
        self
    ) -> str:

        """
        ----------------------------------------
        Get projects.

        Returns
        -------
        str
            Projects.
        ----------------------------------------
        """

        return str(self._projects)

    @projects.setter
    def projects(
        self,
        projects: str
    ):

        """
        ----------------------------------------
        Set username.

        Parameters
        ----------
        projects: str
            Projects.
        ----------------------------------------
        """

        self._projects = projects

    def load_projects(
        self,
    ):

        """
        --------------------------------------------------------------------------------------------------------------------
        Load the user's projects.
        --------------------------------------------------------------------------------------------------------------------
        """

        self.projects = ""

        if (not force_auth()) or (self.validate_usr and self.validate_usr_pwd):

            # Unspecified user: use project-path associations.
            if (self.usr == "root") or (not force_auth()):
                for project_i in st.secrets.project_path:
                    if project_i[KEY_PROJECT] != "context":
                        if self.projects != "":
                            self.projects += ";"
                        self.projects += project_i[KEY_PROJECT]

            # Specified user: use user-projects associations.
            else:
                for user_i in st.secrets.usr_projects:
                    if user_i[KEY_USR] in self.usr:
                        self.projects = user_i[KEY_PROJECTS]
                        break


def path(
    project_code: str
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Get the path for the data directory.

    Parameters
    ----------
    project_code: str
        Project code.

    Returns
    -------
    str
        Path of the data directory.
    --------------------------------------------------------------------------------------------------------------------
    """

    try:

        # Projet-path associations.
        project_l = st.secrets.project_path

        # Locate the projet.
        for project_i in project_l:
            if project_i[KEY_PROJECT] == project_code:

                # Return the path associated with this project.
                return project_i[KEY_PATH]

    except AttributeError:
        pass

    return ""


def force_auth():

    """
    --------------------------------------------------------------------------------------------------------------------
    Determine if the authentication is enabled.

    Returns
    -------
    bool
        If True, authentication is active.
    --------------------------------------------------------------------------------------------------------------------
    """

    if st.secrets.force_auth:
        return True

    return False
