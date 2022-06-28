# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Interaction with Google Drive.
#
# Contact information:
# 1. rousseau.yannick@ouranos.ca (pimping agent)
# (C) 2020-2022 Ouranos, Canada
#
# ----------------------------------------------------------------------------------------------------------------------
#
# 1. Install the following libraries:
#
#    pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib tabulate requests tqdm
#
# 2. Create and configure a Google Cloud project:
#
#    Visit: https://console.cloud.google.com
#
#    IAM & admin > Create a project
#    - Project name = dashboard
#
#    APIs & services > Library
#    - Search: Google Drive API
#    - Enable.
#
#    APIs & services > Credentials > OAuth consent screen
#    - User type = external
#    - App information:
#      . App name           = dashboard
#      . User support email = *@gmail.com
#    - Test users
#      . Email = *@gmail.com
#    - Developer contact information
#      . Email = *@gmail.com
#
#    APIs & services > Credentials > Create credentials > oAuth client ID
#    - Application type = Web
#    - Name = dashboard
#      URI  = see auth_uri in .toml
#    - Results:
#      Put 'client_id' and 'client_secret' in .toml
#
#    Authorize the API
#    - Navigate to the 'auth_uri' (see .toml)
#    - Select Drive API v3.
#      Select the item that corresponds to 'scopes' in .toml
#    - Settings (the wheel in the right corner):
#      OAuth flow             = Server-side
#      OAuth endpoints        = Google
#      Authorization endpoint = https://accounts.google.com/o/oauth2/v2/auth
#      Token endpoint         = https://oauth2.googleapis.com/token
#      Access token location  = Authorization header w/ Bearer prefix
#      Access type            = Offline
#      Force prompt           = Consent screen
#      Use your own OAuth credentials
#      Enter client_id and client_secret
#    - Authorize API
#      Allow... (even if unsafe)
#    - Exchange authorization code for tokens
#      Copy refresh token to clipboard.
#    - Refresh token = see 'refresh_token' in the document of .toml
#
#    IAM & admin > Service accounts:
#    - Create service account:
#      Name       = dashboard
#      Account ID = dashboard
#    - Keys > Add key > Create new key
#      Save JSON and move it to the work directory: see 'json' in .toml
#
# 3. Terminology
#
#    Meaning of variable names in the current module:
#    - item_id : Identifier.
#    - file_id : Identifier of a file.
#    - dir_id  : Identifier of a directory.
#    - root_id : Identifier of a directory that is the root in a given context.
#
#    Google Drive uses the term 'folder' to represent a container (of files. Given that the current module seeks to
#    mimic the behaviour of Unix/Linux, the term used is 'directory'. However, these two terms or equivalent.
#
#    Paths are relative to the root directory.
#
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import io
import json
import pandas as pd
import re
import requests
import streamlit as st
from googleapiclient import errors as google_errors
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from PIL import Image
from typing import List, Optional, Tuple, Union

# Dashboard libraries.
import dash_file_utils as dfu

# Drive information.
API     = "drive"
VERSION = "v3"

# Field properties associated with an item (directory or file).
# Default (in googleapiclient.discovery):
PROP_ID            = "id"            # Item identifier (directory or file).
PROP_NAME          = "name"          # Item name
PROP_PARENTS       = "parents"       # List of (parent ID).
PROP_SIZE          = "size"          # Item size Size.
PROP_MIME_TYPE     = "mimeType"      # Item MIME type.
PROP_MODIFIED_TIME = "modifiedTime"  # Item last modified time.
# Added:
PROP_ITEM_ID       = "item_id"       # Equivalent to 'PROP_ID' (to be more explicit as there are several identifiers).
PROP_PARENT_ID     = "parent_id"     # Equivalent to 'PROP_PARENTS[0]' (only the first one is considered).
PROP_PATH          = "path"          # Path, relative to the root directory.
# Dictionary.
PROPERTIES = {
    "id":             PROP_ID,
    "name":           PROP_NAME,
    "parents":        PROP_PARENTS,
    "size":           PROP_SIZE,
    "mime_type":      PROP_MIME_TYPE,
    "modified_time":  PROP_MODIFIED_TIME,
    "item_id":        PROP_ITEM_ID,
    "parent_id":      PROP_PARENT_ID,
    "path":           PROP_PATH
}

# MIME types (https://developers.google.com/drive/api/guides/mime-types)
MT_AUDIO        = "audio"
MT_DOCUMENT     = "document"
MT_DRIVE_SDK    = "drive-sdk"
MT_DRAWING      = "drawing"
MT_FILE         = "file"
MT_FOLDER       = "folder"
MT_FORM         = "form"
MT_FUSIONTABLE  = "fusiontable"
MT_JAM          = "jam"
MT_MAP          = "map"
MT_PHOTO        = "photo"
MT_PRESENTATION = "presentation"
MT_SCRIPT       = "script"
MT_SHORTCUT     = "shortcut"
MT_SIZE         = "site"
MT_SPREADSHEET  = "spreadsheet"
MT_UNKNOWN      = "unknown"
MT_VIDEO        = "video"
MT_CSV          = "csv"
MIME_TYPES = {
    MT_AUDIO:        "application/vnd.google-apps.audio",
    MT_DOCUMENT:     "application/vnd.google-apps.document",
    MT_DRIVE_SDK:    "application/vnd.google-apps.drive-sdk",
    MT_DRAWING:      "application/vnd.google-apps.drawing",
    MT_FILE:         "application/vnd.google-apps.file",
    MT_FOLDER:       "application/vnd.google-apps.folder",
    MT_FORM:         "application/vnd.google-apps.form",
    MT_FUSIONTABLE:  "application/vnd.google-apps.fusiontable",
    MT_JAM:          "application/vnd.google-apps.jam",
    MT_MAP:          "application/vnd.google-apps.map",
    MT_PHOTO:        "application/vnd.google-apps.photo",
    MT_PRESENTATION: "application/vnd.google-apps.presentation",
    MT_SCRIPT:       "application/vnd.google-apps.script",
    MT_SHORTCUT:     "application/vnd.google-apps.shortcut",
    MT_SIZE:         "application/vnd.google-apps.site",
    MT_SPREADSHEET:  "application/vnd.google-apps.spreadsheet",
    MT_UNKNOWN:      "application/vnd.google-apps.unknown",
    MT_VIDEO:        "application/vnd.google-apps.vide",
    MT_CSV:          "texxt/csv"
}


class GoogleDrive:

    def __init__(
        self,
        root_id: Optional[str] = ""
    ):

        """
        ------------------------------------------
        Constructor.

        Parameters
        ----------
        root_id: Optional[str]
            ID of root directory.
            If it is not specified, the ID of the root directory is used. Otherwise, it can be the ID of any other
            directory under the root directory.
            Any path is related to the root directory.
        ------------------------------------------
        """

        # Drive information.
        self.json          = st.secrets["gd"]["json"]
        self.client_id     = st.secrets["gd"]["client_id"]
        self.client_secret = st.secrets["gd"]["client_secret"]
        self.refresh_token = st.secrets["gd"]["refresh_token"]
        self.auth_url      = st.secrets["gd"]["auth_url"]
        self.api_url       = st.secrets["gd"]["api_url"]
        self.scopes        = st.secrets["gd"]["scopes"]
        # self.access_token = self.access_token(self.client_id, self.client_secret, self.refresh_token)

        # Create credentials.
        service_account_info = json.load(open(self.json))
        creds = Credentials.from_service_account_info(service_account_info, scopes=self.scopes)

        # Create service.
        # Cache discovery is disabled to get rid of the following warning:
        # "file_cache is only supported with oauth2client<4.0.0"
        self.service = build(API, VERSION, credentials=creds, cache_discovery=False)

        # Use the absolute root id if none is provided.
        # TODO: Find out why the list of items comprised in the root directory don't show up when using the 'ls'
        #       function with the absolute 'root_id'.
        self.root_id = root_id
        if self.root_id == "":
            self.root_id = self.service.files().get(fileId="root").execute()["id"]

    @property
    def access_token(
        self
    ) -> str:

        """
        ------------------------------------------
        Create a new Access Token using the Refresh Token and also refreshes the ID Token (see comment below).

        Returns
        -------
        str
            Access token.
        ------------------------------------------
        """

        # Prepare authentication parameters.
        params = {
            "grant_type":    "refresh_token",
            "client_id":     self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }

        # Connect and obtain acces token.
        r = requests.post(self.auth_url, data=params)
        if r.ok:
            return r.json()["access_token"]
        else:
            return ""

    def ls(
        self,
        item_id: Optional[str] = "",
        dir_id: Optional[str] = "",
        mime_type: Optional[str] = ""
    ) -> List:

        """
        ------------------------------------------
        List directory and file names.

        This is the equivalent of the 'ls' command on Linux.

        Parameters
        ----------
        item_id: Optional[str]
            Item (directory or file) ID.
        dir_id: Optional[str]
            Directory ID.
        mime_type: Optional[str]
            Mime type (acronym). It corresponds to the key in the dictionary 'MIME_TYPES'.

        Returns
        -------
        List
            List of directory and file names.
        ------------------------------------------
        """

        # List files.
        df = pd.DataFrame(self.ls_la(item_id=item_id, dir_id=dir_id, mime_type=mime_type))

        # Select and return names.
        return list(df[PROP_NAME])

    def find_ls_dot(
        self,
        item_id: Optional[str] = "",
        dir_id: Optional[str] = "",
        mime_type: Optional[str] = "",
        p_parent: Optional[str] = ""
    ) -> List:

        """
        ------------------------------------------
        List all paths of directories and files.

        This is the equivalent of the 'find ls .' command on Linux.

        Parameters
        ----------
        item_id: Optional[str]
            Item (directory or file) ID.
        dir_id: Optional[str]
            Directory ID.
        mime_type: Optional[str]
            Mime type (acronym). It corresponds to the key in the dictionary 'MIME_TYPES'.
        p_parent: Optional[str]
            Path of parent. This is required in recursive mode.

        Returns
        -------
        List
            List of directory and file names.
        ------------------------------------------
        """

        # List files.
        df = pd.DataFrame(self.ls_la(item_id=item_id, dir_id=dir_id, mime_type=mime_type, recursive=True,
                                     p_parent=p_parent))

        # Select and return names.
        return list(df[PROP_PATH])

    def ls_la(
        self,
        item_id: Optional[str] = "",
        dir_id: Optional[str] = "",
        mime_type: Optional[str] = "",
        recursive: Optional[bool] = False,
        pattern: Optional[str] = "",
        p_parent: Optional[str] = "",
        df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:

        """
        ------------------------------------------
        List directories and files (potentially recursive).

        This is the equivalent of the 'ls -la' command on Linux

        Parameters
        ----------
        item_id: Optional[str]
            Item (directory or file) ID.
        dir_id: Optional[str]
            Directory ID.
        mime_type: Optional[str]
            Mime type (acronym). It corresponds to the key in the dictionary 'MIME_TYPES'.
        recursive: Optional[bool] = False
            If True, search in sub-directory.
        pattern: str
            Pattern.
        p_parent: Optional[str]
            Path of parent. This is required in recursive mode.
        df: Optional[pd.DataFrame]
            DataFrame.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame.
        ------------------------------------------
        """

        # Read items.
        df_items = pd.DataFrame(self.ls_la_not_recursive(dir_id=dir_id, mime_type=mime_type, p_parent=p_parent))

        # Verify if a specific ID was found.
        if item_id != "":
            df_single = df_items[df_items[PROP_ITEM_ID] == item_id]
            if len(df_single) > 0:
                return df_single
            else:
                return pd.DataFrame(None)

        # Search in current directory.
        if df is None:
            df = pd.DataFrame(df_items[0:0])
        for i in range(len(df_items)):
            df_i = pd.DataFrame(df_items[i:(i + 1)])

            # Verify if the pattern matches.
            name = list(df_i[PROP_NAME].values)[0]
            match = re.match(pattern.replace("*", ".*"), name)
            pattern_match = \
                (match is not None) and (match.pos == 0) and (match.endpos == len(name)) and\
                (pattern.count("/") == name.count("/"))

            # No pattern used or the pattern matches.
            if ((pattern == "") and (p_parent == "")) or pattern_match:
                df = pd.concat([df, df_i], axis=0)

        # Search in sub-directory.
        if recursive:

            # Loop through directories.
            df_dirs = df_items[df_items[PROP_MIME_TYPE] == MIME_TYPES[MT_FOLDER]]
            df_dirs.reset_index(inplace=True)
            for i in range(len(df_dirs)):

                # Extract tokens.
                tokens = pattern.split("/")

                # The current directory meets criteria.
                df_i = pd.DataFrame(df_dirs[i:(i + 1)])
                if (pattern == tokens[0] + "/") and (tokens[0] == list(df_i["name"].values)[0]):
                    df = pd.concat([df, df_i], axis=0)

                # Adjust pattern (for child).
                pattern_child = ""
                if pattern != "":
                    pattern_child = pattern.replace(tokens[0] + "/", "", 1)

                # List items.
                if (tokens[0] not in ["", "*", df_dirs[PROP_NAME][i]]) and \
                   ((pattern == pattern_child) and (pattern_child.find("**") != 0)):
                    continue

                df = pd.DataFrame(self.ls_la(item_id=item_id, dir_id=df_dirs[PROP_ITEM_ID][i], mime_type=mime_type,
                                             recursive=recursive, pattern=pattern_child,
                                             p_parent=df_dirs[PROP_PATH][i], df=df))

        # Sort by path.
        if len(df) > 0:
            df = df.sort_values(by=PROP_PATH)
            df["column_id"] = list(range(len(df)))
            df.drop_duplicates(inplace=True)
            df.set_index(["column_id"], inplace=True)

        return df

    def ls_la_not_recursive(
        self,
        dir_id: Optional[str] = "",
        mime_type: Optional[str] = "",
        p_parent: Optional[str] = ""
    ) -> pd.DataFrame:

        """
        ------------------------------------------
        List items within a directory (not recursive).

        Parameters
        ----------
        dir_id: Optional[str]
            Directory ID.
        mime_type: Optional[str]
            Mime type (acronym). It corresponds to the key in the dictionary 'MIME_TYPES'.
        p_parent: Optional[str]
            Path of parent. This is required in recursive mode.

        Returns
        -------
        pd.DataFrame.
            Dataframe.
        ------------------------------------------
        """

        # Specify the ID of the directory to look into if it was not specified.
        if dir_id == "":
            dir_id = self.root_id

        # Item (folder or file) attributes.
        fields = "nextPageToken,incompleteSearch,files(" + PROP_ID + "," + PROP_NAME + "," + PROP_MIME_TYPE + "," +\
            PROP_SIZE + "," + PROP_PARENTS + "," + PROP_MODIFIED_TIME + ")"

        # Query.
        q = "" if dir_id == "" else ("'{}' in " + PROP_PARENTS).format(dir_id)

        # MIME type.
        if mime_type != "":
            if q != "":
                q += " and "
            q += PROP_MIME_TYPE + "='" + MIME_TYPES[mime_type] + "'"

        # List items.
        if q == "":
            kwargs = {"fields": fields}
        else:
            kwargs = {"q": q, "fields": fields}
        response = self.service.files().list(**kwargs).execute()
        items = response["files"]

        # Containers.
        l_item_id, l_name, l_path, l_parent_id, l_size, l_mime_type, l_modified_time = [], [], [], [], [], [], []

        # Loop through items.
        for item in items:

            item_id_i = item[PROP_ID]

            # File ID.
            l_item_id.append(item_id_i)

            # Name.
            name_i = item[PROP_NAME]
            l_name.append(name_i)

            # MIME type.
            mime_type_i = item[PROP_MIME_TYPE]
            l_mime_type.append(mime_type_i)

            # Path.
            path_i = item[PROP_NAME]
            if p_parent != "":
                path_i = p_parent + path_i
            if mime_type_i == MIME_TYPES[MT_FOLDER]:
                path_i += "/"
            l_path.append(path_i)

            # ID of the parent directory.
            try:
                parent_id_i = item[PROP_PARENTS][0]
            except KeyError:
                parent_id_i = None
            l_parent_id.append(parent_id_i)

            # Size (KB, MB).
            # Note that a directory doesn't have any size.
            try:
                size_i = get_size_format(int(item[PROP_SIZE]))
            except KeyError:
                size_i = None
            l_size.append(size_i)

            # Modified date time.
            l_modified_time.append(item[PROP_MODIFIED_TIME])

        # Create DataFrame.
        dict_pd = {
            PROP_ITEM_ID:       l_item_id,
            PROP_NAME:          l_name,
            PROP_PATH:          l_path,
            PROP_PARENT_ID:     l_parent_id,
            PROP_SIZE:          l_size,
            PROP_MIME_TYPE:     l_mime_type,
            PROP_MODIFIED_TIME: l_modified_time
        }
        df = pd.DataFrame(dict_pd)

        return df

    def mkdir(
        self,
        name: str,
        dir_id: Optional[str] = "",
        overwrite: Optional[bool] = False
    ):

        """
        ------------------------------------------
        Create a directory.

        An existing directory will not be created if it already exists, unless the 'overwrite' option is selected.
        Google Drive allows multiples directories with the same name to exist within the same directory. Even if it is
        allowed, the current module seeks to mimic the behaviour of an operating system, on which this is not allowed.

        Parameters
        ----------
        name: str
            Name of directory to create.
        dir_id: Optional[str]
            ID of the directory in which a directory will be created.
        overwrite: Optional[bool]
            If True, overwrite directory.

        Returns
        -------
        str
            Directory ID.
        ------------------------------------------
        """

        # Specify the ID of the directory to look into if it was not specified.
        if dir_id == "":
            dir_id = self.root_id

        # Determine if the directory to create already exists.
        df = pd.DataFrame(self.ls_la(dir_id=dir_id))
        d_exists = len(df[df[PROP_PATH] == name + "/"]) > 0
        if d_exists:

            # Remove directory.
            if overwrite:
                dir_id = str(self.name_to_item_id(name, dir_id))
                self.rm(dir_id)

            # Exit.
            else:
                return ""

        # Create directory.
        if dir_id == "":
            body = {
                PROP_NAME:      name,
                PROP_MIME_TYPE: MIME_TYPES[MT_FOLDER]
            }
        else:
            body = {
                PROP_NAME:      name,
                PROP_PARENTS:   [dir_id],
                PROP_MIME_TYPE: MIME_TYPES[MT_FOLDER]
            }
        response = self.service.files().create(body=body).execute()

        return response[PROP_ITEM_ID]

    def rm(
        self,
        item_id: str
    ):

        """
        ------------------------------------------
        Remove an item (directoryof file).

        Parameters
        ----------
        item_id: str
            Item (directory or file) ID.
        ------------------------------------------
        """

        try:
            self.service.files().delete(fileId=item_id).execute()
            return True

        except google_errors.HttpError:
            return False

    def glob(
        self,
        pattern: str,
        p: Optional[str] = "",
        mime_type: Optional[str] = ""
    ) -> pd.DataFrame:

        """
        ------------------------------------------
        List files with given pattern.

        The search is recursive (looking into subdirectories).
        The directory to look into can be specified (using path).

        This function is the equivalent of 'glob.glob' in Python.

        Parameters
        ----------
        pattern: str
            Pattern.
        p: Optional[str]
            Path.
        mime_type: Optional[str]
            Mime type (acronym). It corresponds to the key in the dictionary 'MIME_TYPES'.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame.
        ------------------------------------------
        """

        # Get item (folder or file) ID.
        dir_id = ""
        if p != "":
            dir_id = str(self.path_to_item_id(p=p))

        df = pd.DataFrame(self.glob_dir_id(pattern=pattern, dir_id=dir_id, mime_type=mime_type))

        return df

    def glob_dir_id(
        self,
        pattern: str,
        dir_id: Optional[str] = "",
        mime_type: Optional[str] = ""
    ) -> pd.DataFrame:

        """
        ------------------------------------------
        List files with given pattern.

        The search is recursive (looking into subdirectories).
        The directory to look into can be specified (using directory ID).

        This function is the equivalent of 'glob.glob' in Python.

        Parameters
        ----------
        pattern: str
            Pattern.
        dir_id: Optional[str]
            ID of directory to look into. If none is specified, search starts at the root.
        mime_type: Optional[str]
            Mime type (acronym). It corresponds to the key in the dictionary 'MIME_TYPES'.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame.
        ------------------------------------------
        """

        # List items (folders and files).
        df = pd.DataFrame(self.ls_la(pattern=pattern, dir_id=dir_id, mime_type=mime_type, recursive=True))

        return df

    def copy(
        self,
        p: str,
        d_parent_id: Optional[str] = ""
    ):

        """
        ------------------------------------------
        TODO: Copy an item (directory or file) to Google Drive. This could help deploy the data.

        If no parent directory ID is provided (or none exists), the directorey is created at the root.

        Parameters
        ----------
        p: str
            Path.
        d_parent_id: Optional[str]
            Parent directory ID.
        ------------------------------------------
        """

        return

    def load_ini(
        self,
        file_id: str
    ) -> str:

        """
        ------------------------------------------
        Load a INI file.

        Parameters
        ----------
        file_id: str
            File ID.

        Returns
        -------
        str
            Content of INI file.
        ------------------------------------------
        """

        url = self.api_url + file_id + "?alt=media"
        res = requests.get(url, headers={"Authorization": "Bearer " + self.access_token})

        return res.text

    def load_csv(
        self,
        file_id: Optional[str] = "",
        path: Optional[str] = ""
    ) -> pd.DataFrame:

        """
        ------------------------------------------
        Load a CSV file.

        The file ID or path must be specified. If both are specified, file ID has priority.

        Parameters
        ----------
        file_id: Optional[str]
            File ID.
        path: Optional[str]
            Path.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame.
        ------------------------------------------
        """

        df = None

        # File ID is not available, but the path is available.
        if (file_id == "") and (path != ""):
            df_items = pd.DataFrame(self.glob(pattern=path))
            if len(df_items) > 0:
                file_id = list(df_items[PROP_ITEM_ID].values)[0]

        # File ID is available.
        if file_id != "":
            url = self.api_url + file_id + "?alt=media"
            res = requests.get(url, headers={"Authorization": "Bearer " + self.access_token})
            df = pd.read_csv(io.StringIO(res.text))

        return df

    def load_image(
        self,
        file_id: Optional[str] = "",
        path: Optional[str] = ""
    ) -> Image:

        """
        --------------------------------------------------------------------------------------------------------------------
        Load an image file.

        The file ID or path must be specified. If both are specified, file ID has priority.

        Parameters
        ----------
        file_id: Optional[str]
            File ID.
        path: Optional[str]
            Path.

        Returns
        -------
        Image.
            Image.
        --------------------------------------------------------------------------------------------------------------------
        """

        image = None

        # File ID is not available, but the path is available.
        if (file_id == "") and (path != ""):
            df_items = pd.DataFrame(self.glob(pattern=path))
            if len(df_items) > 0:
                file_id = list(df_items[PROP_ITEM_ID].values)[0]

        # File ID is available.
        if file_id != "":
            url = self.api_url + file_id + "?alt=media"
            res = requests.get(url, headers={"Authorization": "Bearer " + self.access_token})
            image = Image.open(io.BytesIO(res.content))

        return image

    def load_geojson(
        self,
        file_id: Optional[str] = "",
        path: Optional[str] = "",
        out_format: str = "vertices-coords"
    ) -> Union[pd.DataFrame, Tuple[List[float], any]]:

        """
        --------------------------------------------------------------------------------------------------------------------
        Load a geojson file.

        The file ID or path must be specified. If both are specified, file ID has priority.

        Parameters
        ----------
        file_id: Optional[str]
            File ID.
        path: Optional[str]
            Path.
        out_format: str
            Format = {"vertices-coordinates", "pandas"}

        Returns
        -------
        Union[pd.DataFrame, Tuple[List[float]]]
            Vertices and coordinates, or dataframe.
        --------------------------------------------------------------------------------------------------------------------
        """

        df = None

        # File ID is not available, but the path is available.
        if (file_id == "") and (path != ""):
            df_items = pd.DataFrame(self.glob(pattern=path))
            if len(df_items) > 0:
                file_id = list(df_items[PROP_ITEM_ID].values)[0]

        # File ID is available.
        if file_id != "":
            url = self.api_url + file_id + "?alt=media"
            res = requests.get(url, headers={"Authorization": "Bearer " + self.access_token})
            df = dfu.load_geojson(res, out_format)

        return df

    def item_id_to_path(
        self,
        item_id: str
    ) -> str:

        """
        ------------------------------------------
        Convert the ID of an item (directory or file) to a path.

        Parameters
        ----------
        item_id: str
            Item (directory or file) ID.

        Returns
        -------
        str
            Path.
        ------------------------------------------
        """

        # Extract parent ID.
        df = pd.DataFrame(self.ls_la(item_id=item_id))
        if len(df) > 0:
            return str(df[PROP_PATH].values[0])

        return ""

    def path_to_item_id(
        self,
        p: str,
        dir_id: Optional[str] = ""
    ) -> str:

        """
        ------------------------------------------
        Convert a path to an item (directory or file) ID.

        Parameters
        ----------
        p: str
            Path.
        dir_id: Optional[str]
            ID of the directory to look into.

        Returns
        -------
        str
            Item (directory or file) ID.
        ------------------------------------------
        """

        # Specify the ID of the directory to look into if it was not specified.
        if dir_id == "":
            dir_id = self.root_id

        # Extract item (directory or file) name.
        item = p.split("/")[0]

        # Select the current item (directory or file).
        df = pd.DataFrame(self.ls_la(dir_id=dir_id, recursive=True))
        df_item = df[df[PROP_PATH] == item]
        if len(df_item) == 0:
            df_item = df[df[PROP_PATH] == item + "/"]

        # Item found.
        if len(df_item) > 0:

            # Branch found (directory): need to dig.
            if MT_FOLDER in str(df_item[PROP_MIME_TYPE].values):
                p_inner = p.replace(item + "/", "", 1)
                dir_id_parent_inner = str(df_item[PROP_ITEM_ID].values[0])
                if p_inner == "":
                    return dir_id_parent_inner
                else:
                    return str(self.path_to_item_id(p_inner, dir_id_parent_inner))

            # Leaf found (directory or file): work done.
            else:
                return str(df_item[PROP_ITEM_ID].values[0])

        return ""

    def name_to_item_id(
        self,
        name: str,
        dir_id: Optional[str] = ""
    ) -> str:

        """
        ------------------------------------------
        Convert path to item (directory or file) ID.

        Parameters
        ----------
        name: str
            Name.
        dir_id: Optional[str]
            ID of directory to look into.

        Returns
        -------
        str
            Item (directory or file) ID.
        ------------------------------------------
        """

        # Specify a directory if it was not specified.
        if dir_id == "":
            dir_id = self.root_id

        # List items (directories and files).
        df = pd.DataFrame(self.ls_la(dir_id=dir_id))

        # Search for the item.
        df_f = df[df[PROP_NAME] == name]
        if len(df_f) > 0:
            return str(df_f[PROP_ITEM_ID].values[0])

        return ""

    def item_id_to_name(
        self,
        item_id: str
    ) -> str:

        """
        ------------------------------------------
        Convert item (directory or file) ID to name.

        Parameters
        ----------
        item_id: str
            Item (directory or file) ID.

        Returns
        -------
        str
            Name.
        ------------------------------------------
        """

        df = pd.DataFrame(self.ls_la(dir_id=self.root_id))
        df_f = df[df[PROP_ITEM_ID] == item_id]
        if len(df_f) > 0:
            return str(df_f[PROP_PATH].values[0])

        return ""


def get_size_format(
    b: int,
    factor: Optional[int] = 1024,
    suffix: Optional[str] = "B"
) -> str:

    """
    --------------------------------------------------------------------------------------------------------------------
    Scale bytes to its proper byte format.

    Examples
    --------
    1253656 => '1.20MB'
    1253656678 => '1.17GB'

    Parameters
    ----------
    b: int
        Number of bytes.
    factor: Optional[int]
        Factor: minimum number of items required to justify the use of a larger unit.
    suffix: Optional[str]
        Suffix. The default value stands for bytes.

    Returns
    -------
    str
        Size, as a string.
    --------------------------------------------------------------------------------------------------------------------
    """

    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor

    return f"{b:.2f}Y{suffix}"
