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
    view = st.sidebar.radio("Choisir la vue", plot.view_list)
    plot_lib = st.sidebar.radio("Choisir la librairie visuelle", plot.plot_libs)
        
    if view == plot.view_list[0]:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("ts"))
        if plot_lib == "altair": 
            st.write(plot.gen_ts(vars, "altair"))
        elif plot_lib == "hvplot": 
            st.write(hv.render(plot.gen_ts(vars, "hvplot")), backend="bokeh")
        else:
            st.write(plot.gen_ts(vars, "matplotlib"))
            
    elif view == plot.view_list[1]:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("tbl"))
        hors = st.selectbox("Horizon", options=utils.get_hor_list(vars, "tbl", False))
        df_tbl = plot.gen_tbl(vars, hors)
        ref = str(plot.get_ref_val(vars))
        if vars in ["tasmin", "tasmax"]:
            df_tbl = df_tbl.style.format("{:.1f}")
            ref = "{:.1f}".format(float(ref))
        st.table(df_tbl)
        st.write("Valeur de référence : " + ref)
        
    else:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("map"))


main()