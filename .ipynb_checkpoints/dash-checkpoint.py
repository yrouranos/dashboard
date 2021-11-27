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
import rcp_def
import streamlit as st
import varidx_def as vi
import view_def
from PIL import Image


def main():

    """
    --------------------------------------------------------------------------------------------------------------------
    Entry point.
    --------------------------------------------------------------------------------------------------------------------
    """
  
    # Create context.
    cntx = context_def.Context()

    st.sidebar.image(Image.open(cf.p_logo), width=150)  
        
    # Views.    
    cntx.views = view_def.Views()
    views = st.sidebar.radio("Choisir la vue", cntx.views.get_desc_l())
    cntx.view = view_def.View(cntx.views.get_code(views.value))
    
    # Plotting libraries.
    cntx.libs = lib_def.Libs(cntx.view.get_name())
    if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_map]:
        libs = st.sidebar.radio("Choisir la librairie visuelle", cntx.libs.get_desc_l())
        cntx.lib = lib_def.Lib(cntx.libs.get_code(libs.value))
    
    # Variables and indices.
    cntx.varidxs = vi.VarIdxs(cntx.view.get_code())
    vars = st.selectbox("Variable", options=cntx.varidxs.get_desc_l())
    cntx.varidx = vi.VarIdx(cntx.vi.get_code(varidxs.value))
        
    # Horizons.
    cntx.hors = hor_def.Hors(cntx)
    if cntx.view.get_code() in [view_def.mode_tbl, view_def.mode_map]:
        hors = st.selectbox("Horizon", options=cntx.hors.get_cesc_l())
        cntx.hor = hor_def.Hor(cntx.hors.get_code(hors.value))
        
    # Emission scenarios.
    cntx.rcps = rcp_def.RCPs(cntx, cf.d_data)
    cntx.rcp = rcp_def.RCP(cntx.rcps.get_code(rcps.value))
    
    # Components.
    if cntx.view.get_code() == view_def.mode_ts:
        if cntx.lib.get_code() in [plib.mode_alt, plib.mode_mat]: 
            st.write(plot.gen_ts(cntx))
        else:
            st.write(hv.render(plot.gen_ts(cntx)), backend="bokeh")
            
    elif cntx.view.get_code() == view_def.mode_tbl:
        tbl = plot.gen_tbl(cntx)
        tbl_ref = str(plot.get_ref_val(cntx))
        if vars in [vi.var_tas, vi.var_tasmin, vi.var_tasmax]:
            tbl = tbl.style.format("{:.1f}")
            tbl_ref = "{:.1f}".format(float(tbl_ref))
        st.table(tbl)
        st.write("Valeur de référence : " + tbl_ref)
        
    else:
        st.write(plot.gen_map(cntx, "quantile", cf.q_l[0]))
        st.write(plot.gen_map(cntx, "quantile", cf.q_l[1]))


main()