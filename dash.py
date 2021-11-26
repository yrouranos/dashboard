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
import context
import ghg_scen
import holoviews as hv
import plot
import streamlit as st
import utils
from PIL import Image


def main():

    """
    --------------------------------------------------------------------------------------------------------------------
    Entry point.
    --------------------------------------------------------------------------------------------------------------------
    """
  
    # Create context.
    cntx = context.Context()
    
    st.sidebar.image(Image.open(cf.p_logo), width=150)

    views = st.sidebar.radio("Choisir la vue", list(cf.views.values()))

    vars = st.selectbox("Variable", options=utils.get_varidx_l(utils.get_view_code(views)))
    
    if utils.get_view_code(views) == "ts":
        libs = st.sidebar.radio("Choisir la librairie visuelle", cf.libs)  
        cntx.rcps = ghg_scen.RCPs(cf.d_data, vars, "ts")
        if libs == "altair": 
            st.write(plot.gen_ts(vars, cntx.rcps, "altair"))
        elif libs == "hvplot": 
            st.write(hv.render(plot.gen_ts(vars, cntx.rcps, "hvplot")), backend="bokeh")
        else:
            st.write(plot.gen_ts(vars, cntx.rcps, "matplotlib"))
            
    elif utils.get_view_code(views) == "tbl":
        hors = st.selectbox("Horizon", options=utils.get_hor_l(vars, "tbl"))
        cntx.rcps = ghg_scen.RCPs(cf.d_data, vars, "tbl", hors)
        tbl = plot.gen_tbl(vars, cntx.rcps, hors)
        tbl_ref = str(plot.get_ref_val(vars))
        if vars in ["tasmin", "tasmax"]:
            tbl = tbl.style.format("{:.1f}")
            tbl_ref = "{:.1f}".format(float(tbl_ref))
        st.table(tbl)
        st.write("Valeur de référence : " + tbl_ref)
        
    else:
        libs = st.sidebar.radio("Choisir la librairie visuelle", [cf.libs[2]])
        hors = st.selectbox("Horizon", options=utils.get_hor_l(vars, "map"))
        cntx.rcps = ghg_scen.RCPs(cf.d_data, vars, "map", hors)
        rcps = st.selectbox("Scénario d'émissions", options=cntx.rcps.get_desc_l())
        st.write(plot.gen_map(vars, hors, cntx.rcps.get_name(rcps), "quantile", cf.q_l[0]))
        st.write(plot.gen_map(vars, hors, cntx.rcps.get_name(rcps), "quantile", cf.q_l[1]))


main()