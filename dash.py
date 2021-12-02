# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Streamlit entry point.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import config as cf
import context_def
import holoviews as hv
import hor_def
import lib_def
import plot
import project_def
import rcp_def
import stat_def
import streamlit as st
import utils
import varidx_def as vi
import view_def
from PIL import Image

cntx = None


def refresh():

    """
    --------------------------------------------------------------------------------------------------------------------
    Refresh GUI.
    --------------------------------------------------------------------------------------------------------------------
    """

    global cntx

    # Initialize context.
    if cntx is None:
        cntx = context_def.Context()
        cntx.platform = "streamlit"
        cntx.views = view_def.Views()
        cntx.libs = lib_def.Libs()
        cntx.varidxs = vi.VarIdxs()
        cntx.hors = hor_def.Hors()
        cntx.rcps = rcp_def.RCPs()
        cntx.stats = stat_def.Stats()
        cntx.project = project_def.Project("sn")
        stat_def.mode_q_low = "q" + cntx.project.get_quantiles_as_str()[0]
        stat_def.mode_q_high = "q" + cntx.project.get_quantiles_as_str()[1]

    st.sidebar.image(Image.open(utils.get_p_logo(cntx)), width=150)
        
    # Views.
    cntx.views = view_def.Views(cntx)
    views = st.sidebar.radio("Choisir la vue", cntx.views.get_desc_l())
    cntx.view = view_def.View(cntx.views.get_code(views))
    
    # Plotting libraries.
    cntx.libs = lib_def.Libs(cntx.view.get_code())
    libs = st.sidebar.radio("Choisir la librairie visuelle", options=cntx.libs.get_desc_l())
    cntx.lib = lib_def.Lib(cntx.libs.get_code(libs))

    # Deltas.
    st.sidebar.markdown("<style>.sel_title {font-size:14.5px}</style>", unsafe_allow_html=True)
    st.sidebar.markdown("<p class='sel_title'>Afficher les anomalies</p>", unsafe_allow_html=True)
    deltas = st.sidebar.checkbox("", value=False)
    cntx.delta = deltas

    # Variables and indices.
    cntx.varidxs = vi.VarIdxs(cntx)
    varidxs = st.selectbox("Variable", options=cntx.varidxs.get_desc_l())
    cntx.varidx = vi.VarIdx(cntx.varidxs.get_code(varidxs))
        
    # Horizons.
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        cntx.hors = hor_def.Hors(cntx)
        hors = st.selectbox("Horizon", options=cntx.hors.get_code_l())
        cntx.hor = hor_def.Hor(hors)
        
    # Emission scenarios.
    cntx.rcps = rcp_def.RCPs(cntx)
    if cntx.view.get_code() == view_def.mode_map:
        rcps = st.selectbox("Scénario d'émissions", options=cntx.rcps.get_desc_l())
        cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcps))

    # Statistics.
    if cntx.view.get_code() == view_def.mode_map:
        cntx.stats = stat_def.Stats(cntx)
    if cntx.view.get_code() == view_def.mode_map:
        stats = st.selectbox("Statistique", options=cntx.stats.get_desc_l())
        cntx.stat = stat_def.Stat(cntx.stats.get_code(stats))

    # Components.
    if cntx.view.get_code() == view_def.mode_ts:
        if cntx.lib.get_code() in [lib_def.mode_alt, lib_def.mode_mat]:
            st.write(plot.gen_ts(cntx))
        else:
            st.write(hv.render(plot.gen_ts(cntx)), backend="bokeh")
    elif cntx.view.get_code() == view_def.mode_tbl:
        st.write(plot.gen_tbl(cntx))
    else:
        st.write(plot.gen_map(cntx))
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
        tbl_ref = plot.get_ref_val(cntx)
        st.write("Valeur de référence : " + tbl_ref)


refresh()
