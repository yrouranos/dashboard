import config as cf
import holoviews as hv
import plot
import streamlit as st
import utils
from PIL import Image


def main():

    """
    Entry point.
    """
  
    logo_oura = Image.open(cf.p_logo)
    
    st.sidebar.image(logo_oura, width=150)

    views = st.sidebar.radio("Choisir la vue", list(cf.views.values()))

    vars = st.selectbox("Variable", options=utils.get_varidx_list(utils.get_view_code(views)))
    
    if utils.get_view_code(views) == "ts":
        libs = st.sidebar.radio("Choisir la librairie visuelle", cf.libs)        
        if libs == "altair": 
            st.write(plot.gen_ts(vars, "altair"))
        elif libs == "hvplot": 
            st.write(hv.render(plot.gen_ts(vars, "hvplot")), backend="bokeh")
        else:
            st.write(plot.gen_ts(vars, "matplotlib"))
            
    elif utils.get_view_code(views) == "tbl":
        hors = st.selectbox("Horizon", options=utils.get_hor_list(vars, "tbl"))
        tbl = plot.gen_tbl(vars, hors)
        tbl_ref = str(plot.get_ref_val(vars))
        if vars in ["tasmin", "tasmax"]:
            tbl = tbl.style.format("{:.1f}")
            tbl_ref = "{:.1f}".format(float(tbl_ref))
        st.table(tbl)
        st.write("Valeur de référence : " + tbl_ref)
        
    else:
        libs = st.sidebar.radio("Choisir la librairie visuelle", [cf.libs[2]])
        hors = st.selectbox("Horizon", options=utils.get_hor_list(vars, "map"))
        rcps = st.selectbox("Scénario d'émissions", options=utils.get_rcp_list(vars, "map", hors))
        st.write(plot.gen_map(vars, hors, rcps, "quantile", cf.q_list[0]))
        st.write(plot.gen_map(vars, hors, rcps, "quantile", cf.q_list[1]))


main()