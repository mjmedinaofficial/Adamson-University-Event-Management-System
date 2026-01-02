import streamlit as st
import pandas as pd
import pyodbc
from utils import run_query, execute_update

st.set_page_config(page_title="Add Location", layout="wide")
st.title("Add Location")
st.write("Welcome to Event add_location.py")
st.divider()

with st.form("add_location_form"):
    col1,col2 = st.columns(2)
    with col1:
        new_localtion_name = st.text_input("Location Name")
        new_localtion_type = st.selectbox("Location Type",["Outdoor","Indoor"])
        new_localtion_capacity = st.text_input("Location Capacity")
        new_localtion_address = st.text_area("Location Address",height=100)
        
    with col2:
        new_localtion_ct_person = st.text_input("Contact Person")
        new_localtion_ct_phone = st.text_input("Contact Number")
        new_localtion_status = st.selectbox("Status",["Unavailable","Available"])
    
    submited_btn = st.form_submit_button("Submit")
    
    if submited_btn:
        if not new_localtion_name or not new_localtion_ct_phone:
            st.warning("Please fill in the Location Name and Contact number.")
        else:
            sql_query= """
                INSERT INTO Location
                (loc_name,loc_address,loc_capacity,loc_status,loc_type,loc_contact_person,loc_phone)
                VALUES (?,?,?,?,?,?,?)
            """
            params = (new_localtion_name, new_localtion_address, new_localtion_capacity,
                      new_localtion_status, new_localtion_type, new_localtion_ct_person, new_localtion_ct_phone)
            
            if execute_update(sql_query,params):
                st.success(f"Success! Event '{new_localtion_name}' has been added.")