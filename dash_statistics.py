# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
#
# Statistics functions.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

# Dashboard libraries.
import dash_utils as du
import def_sim
from def_constant import const as c
from def_context import cntx


def calc_clusters(
    n_cluster: int,
    format_nicely: bool = True
) -> pd.DataFrame:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate cluster table (based on time series).

    Parameters
    ----------
    n_cluster: int
        Number of clusters.
    format_nicely: bool
        Format nicely (for display)

    Returns
    -------
    pd.DataFrame
    --------------------------------------------------------------------------------------------------------------------
    """

    # Tells whether to normalize values or not (between 0 and 1).
    normalize = True

    # Tells whether to take all years as attributes. The opposite is to take a few quantiles representing these years.
    years_as_attributes = False

    # Identify the simulations that shared between variables.
    sim_l = du.get_shared_sims()

    # Normalize data.
    def norm(df: pd.DataFrame) -> pd.DataFrame:
        min_val = np.nanmin(df.values)
        max_val = np.nanmax(df.values)
        df = (df - min_val) / (max_val - min_val)
        return df

    # Dataset holding absolute values.
    df_abs = pd.DataFrame()

    # Load dataset for the current variable.
    def load() -> pd.DataFrame:

        # Load and format dataset.
        df = pd.DataFrame(du.load_data("sim"))
        df = df[np.isnan(df[c.ref]) == False]
        df["year"] = df["year"].astype(str)
        df.drop([c.ref], axis=1, inplace=True)

        # Select the columns associated with the current RPC.
        rcp_code = cntx.rcp.code if cntx.rcp is not None else ""
        if rcp_code != c.rcpxx:
            df_tmp = df[["year"]]
            for column in df.columns:
                if (rcp_code in column) and (column in sim_l):
                    df_tmp[column] = df[column]
            df = df_tmp

        # Transpose.
        df = df.transpose()
        columns = df.iloc[0]
        df = df[1:]
        df.columns = columns

        # Sort by simulation name.
        df["sim"] = df.index
        df.sort_values(by="sim", inplace=True)
        df.drop(columns=["sim"], inplace=True)

        # Set mean and quantiles as attributes.
        n_columns = len(columns)
        df["q50"] = df.iloc[:, 0:n_columns].quantile(q=0.5, axis=1, numeric_only=False, interpolation="linear")
        if not years_as_attributes:
            df["q10"] = df.iloc[:, 0:n_columns].quantile(q=0.1, axis=1, numeric_only=False, interpolation="linear")
            df["q90"] = df.iloc[:, 0:n_columns].quantile(q=0.9, axis=1, numeric_only=False, interpolation="linear")
            df = df[["q10", "q50", "q90"]]

        # Update the dataframe holding absolute values.
        df_abs[cntx.varidx.code] = df["q50"]
        if len(df_abs.columns) == 1:
            df_abs.index = df.index

        # Normalize data.
        if normalize:
            df = norm(df)

        return df

    # Calculate the normalized values, combining all variables.
    df_res = None
    for i in range(cntx.varidxs.count):
        cntx.varidx = cntx.varidxs.items[i]
        df_i = load()
        df_res = df_i if df_res is None else (df_res + df_i ** 2)
    df_res = df_res ** 0.5
    df_res = df_res.dropna()
    indices = df_res.index

    # Normalize data.
    if normalize:
        df_res = norm(df_res)

    # Perform clustering.
    ac = AgglomerativeClustering(n_clusters=n_cluster, affinity="euclidean", linkage="ward").fit(df_res)
    groups = ac.fit_predict(df_res)
    df_res["Moyenne"] = df_res["q50"]
    df_res["Groupe"] = groups + 1

    # Format table.
    df_format = pd.DataFrame(indices)
    df_format["RCP"] = [""] * len(df_format)
    df_format["Groupe"] = groups + 1
    var_code_l = cntx.varidxs.code_l
    for var_code in var_code_l:
        df_format[var_code] = df_abs[var_code].values
    df_format.sort_values(by="Groupe", inplace=True)
    df_format.columns = ["Simulation", "RCP", "Groupe"] + var_code_l
    for i in range(len(df_format)):
        sim = def_sim.Sim(df_format["Simulation"][i])
        df_format["Simulation"][i] = sim.rcm + "_" + sim.gcm
        df_format["RCP"][i] = sim.rcp.desc

    return df_format
