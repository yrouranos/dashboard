import streamlit as st
import plot
import utils
from PIL import Image


def main():

    """
    Entry point.
    """
  
    logo_oura = Image.open(utils.p_logo)
    st.sidebar.image(logo_oura, width=150)
    view = st.sidebar.radio("Select view", plot.view_list)
    plot_lib = st.sidebar.radio("Select plotting library", plot.plot_libs)
        
    if view == plot.view_list[0]:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("ts"))
        if plot_lib == "altair": 
            st.write(plot.gen_ts(vars, "altair"))
        else:
            st.write(plot.gen_ts(vars, "matplotlib"))
    elif view == plot.view_list[1]:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("tbl"))
        st.table(plot.gen_tbl(vars))
    else:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("map"))


main()