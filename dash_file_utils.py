# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Utility functions for file manipulation.
#
# Contact information:
# 1. rousseau.yannick@ouranos.ca (pimping agent)
# (C) 2020-2022 Ouranos, Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import io
import numpy as np
import os
import pandas as pd
import requests
import simplejson
from pathlib import Path
from typing import List, Tuple, Union

# Dashboard libraries.
from cl_constant import const as c


def p_exists(
    p: str
) -> bool:

    """
    --------------------------------------------------------------------------------------------------------------------
    Determine whether a path exists or not.

    Parameters
    ----------
    p: str
        Path.

    Returns
    -------
    bool
        True if a path exists.
    --------------------------------------------------------------------------------------------------------------------
    """

    if ("http" in p) or ("ftp" in p):
        return requests.head(p, allow_redirects=True).status_code == 200
    else:
        return os.path.exists(p)


def ls_dir(
    p: str
) -> List[str]:
    """
    --------------------------------------------------------------------------------------------------------------------
    List sub-directories within a directory.

    Parameters
    ----------
    p: str
        Path.

    Returns
    -------
    List[str]
        List of sub-directories.
    --------------------------------------------------------------------------------------------------------------------
    """

    dir_l = []

    for e in Path(p).iterdir():
        try:
            if Path(e).is_dir():
                dir_l.append(os.path.basename(str(e)))
        except NotADirectoryError:
            pass

    return dir_l


def load_geojson(
    p: Union[str, requests.Response],
    out_format: str = "vertices-coords"
) -> Union[pd.DataFrame, Tuple[List[float], any]]:

    """
    --------------------------------------------------------------------------------------------------------------------
    Load a geojson file.

    Parameters
    ----------
    p: Union[str, requests.Response]
        Path or HTTP response.
    out_format: str
        Format = {"vertices-coordinates", "pandas"}

    Returns
    -------
    Union[pd.DataFrame, Tuple[List[float]]]
        Vertices and coordinates, or dataframe.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Read file.
    if isinstance(p, str):
        f = open(p)
    else:
        f = io.StringIO(p.text)
    pydata = simplejson.load(f)

    # Extract vertices.
    coords = pydata["features"][0]["geometry"]["coordinates"][0]
    vertices = coords[0]
    if len(vertices) == 2:
        coords = pydata["features"][0]["geometry"]["coordinates"]
        vertices = coords[0]
    if out_format == "vertices":
        return vertices, coords

    # Create dataframe.
    df = pd.DataFrame()
    df[c.DIM_LONGITUDE] = np.array(vertices).T.tolist()[0]
    df[c.DIM_LATITUDE] = np.array(vertices).T.tolist()[1]

    return df
