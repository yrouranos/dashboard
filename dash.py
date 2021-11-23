import holoviews as hv
import plot
import streamlit as st
import utils
from PIL import Image


def main():

    """
    Entry point.
    """
  
    logo_oura = Image.open(utils.p_logo)
    st.sidebar.image(logo_oura, width=150)
    view = st.sidebar.radio("Choisir la vue", list(utils.views.values()))
    plot_lib = st.sidebar.radio("Choisir la librairie visuelle", plot.plot_libs)
        
    if utils.get_view_code(view) == "ts":
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("ts"))
        if plot_lib == "altair": 
            st.write(plot.gen_ts(vars, "altair"))
        elif plot_lib == "hvplot": 
            st.write(hv.render(plot.gen_ts(vars, "hvplot")), backend="bokeh")
        else:
            st.write(plot.gen_ts(vars, "matplotlib"))
            
    elif utils.get_view_code(view) == "tbl":
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("tbl"))
        hors = st.selectbox("Horizon", options=utils.get_hor_list(vars, "tbl"))
        tbl = plot.gen_tbl(vars, hors)
        tbl_ref = str(plot.get_ref_val(vars))
        if vars in ["tasmin", "tasmax"]:
            tbl = df_tbl.style.format("{:.1f}")
            tbl_ref = "{:.1f}".format(float(ref))
        st.table(tbl)
        st.write("Valeur de référence : " + tbl_ref)
        
    else:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("map"))
        hors = st.selectbox("Horizon", options=utils.get_hor_list(vars, "map"))
        rcps = st.selectbox("Scénario d'émissions", options=utils.get_rcp_list(vars, "map", hors))
        st.write(plot.gen_map(vars, hors, rcps, "quantile", utils.q_list[0]))
        st.write(plot.gen_map(vars, hors, rcps, "quantile", utils.q_list[1]))


main()