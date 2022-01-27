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
    n_cluster: int
) -> pd.DataFrame:

    """
    --------------------------------------------------------------------------------------------------------------------
    Generate cluster table (based on time series).

    Parameters
    ----------
    n_cluster: int
        Number of clusters.

    Returns
    -------
    pd.DataFrame
    --------------------------------------------------------------------------------------------------------------------
    """

    # Column names.
    col_year = "year"
    col_sim = "Simulation"
    col_rcp = "RCP"
    col_grp = "Groupe"

    # Tells whether to normalize values or not (between 0 and 1).
    normalize = True

    # Tells whether to take all years as attributes. The opposite is to take a few quantiles representing these years.
    use_years = False

    # Quantiles to consider (in addition of the median).
    use_quantiles = (not use_years) or (cntx.varidxs.count == 1)
    q_l     = cntx.project.quantiles
    q_str_l = np.char.add("q", cntx.project.quantiles_as_str)

    # Column that will hold the representative value (mean or middle quantile).
    column_rep = q_str_l[int((len(q_str_l) - 1) / 2)] if use_quantiles else c.stat_mean

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
        df[col_year] = df[col_year].astype(str)
        df.drop([c.ref], axis=1, inplace=True)

        # Select the columns associated with the current RPC.
        rcp_code = cntx.rcp.code if cntx.rcp is not None else ""
        if rcp_code != c.rcpxx:
            df_tmp = df[[col_year]]
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
        df[col_sim] = df.index
        df.sort_values(by=col_sim, inplace=True)
        df.drop(columns=[col_sim], inplace=True)

        # Set quantiles as attributes.
        n_columns = len(columns)
        if not use_years:
            if use_quantiles:
                for _i in range(0, len(q_l)):
                    df[q_str_l[_i]] =\
                        df.iloc[:, 0:n_columns].quantile(q=q_l[_i], axis=1, numeric_only=False, interpolation="linear")
                df = df[q_str_l]
            else:
                df[c.stat_mean] = df.iloc[:, 0:n_columns].mean(axis=1)
                df = df[c.stat_mean]

        # Update the dataframe holding absolute values (use middle quantile.
        df_abs[cntx.varidx.code] = df[column_rep]
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
        if df_res is None:
            df_res = df_i[[column_rep]]
            df_res.columns = [cntx.varidx.code]
        df_res[cntx.varidx.code] = df_i[column_rep]
    df_res = df_res.dropna()
    indices = df_res.index

    # Perform clustering.
    ac = AgglomerativeClustering(n_clusters=n_cluster, affinity="euclidean", linkage="ward").fit(df_res)
    groups = ac.fit_predict(df_res)

    # Format table.
    df_format = pd.DataFrame(indices)
    df_format[col_rcp] = [""] * len(df_format)
    df_format[col_grp] = groups + 1
    var_code_l = cntx.varidxs.code_l
    for var_code in var_code_l:
        df_format[var_code] = df_abs[var_code].values
    df_format.sort_values(by=col_grp, inplace=True)
    df_format.columns = [col_sim, col_rcp, col_grp] + var_code_l
    for i in range(len(df_format)):
        sim = def_sim.Sim(df_format[col_sim][i])
        df_format[col_sim][i] = sim.rcm + "_" + sim.gcm
        df_format[col_rcp][i] = sim.rcp.desc

    return df_format