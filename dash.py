import streamlit as st
import utils
from PIL import Image


def main():

    """
    Entry point.
    """
  
    logo_oura = Image.open(utils.p_logo)
    st.sidebar.image(logo_oura, width=150)
    views = st.sidebar.radio("Select view", utils.view_list)
    
    if views == utils.view_list[0]:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("ts"))
        st.write(utils.gen_ts(vars))
    elif views == utils.view_list[1]:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("tbl"))
        st.table(utils.gen_tbl(vars))
    else:
        vars = st.selectbox("Variable", options=utils.get_var_or_idx_list("map"))


main()