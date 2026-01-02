import streamlit as st
import pandas as pd
import pyodbc
from utils import run_query, execute_update

st.set_page_config(page_title="Location list", layout="wide")
st.title("Location List")
st.write("Welcome to Event location_list.py")
st.divider()

col_search, col_add = st.columns([3,1])
with col_search:
    search_term = st.text_input("Search by Location name", placeholder="Type to search")

with col_add:
    st.write(""); st.write("")
    if st.button("Quick Add", use_container_width=True):
        st.switch_page("add_location.py")
st.divider()

try:
    fetch_sql = """
        SELECT location_id,loc_name,loc_type,loc_capacity,
        loc_address,loc_contact_person,loc_phone,loc_status
        FROM Location
    """
    rows = run_query(fetch_sql)
    columns = ["ID","Name","Type","Capacity","Address","Contact Person","Phone","Status"]
    df = pd.DataFrame.from_records(rows,columns=columns)
    
    if search_term:
        df = df[df["Name"].str.contains(search_term,case=False,na=False)]
        
    st.caption(f"Find {len(df)} Location")
    
    event = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
    
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        selected_row = df.iloc[selected_index]
        current_id = int(selected_row["ID"])
        current_name = selected_row["Name"]
        
        st.info(f"You selected: **{current_name}**")
        
        tab_view, tab_edit, tab_delete = st.tabs(["Location Details","Update Location","Delete Location"])
        
        with tab_view:
            st.json(selected_row.to_dict())
            
        with tab_edit:
            with st.form("edit_location_form"):
                c1,c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Location Name", value=selected_row["Name"])
                    new_type = st.selectbox("Type", ["Outdoor", "Indoor"], index=0 if selected_row["Type"] == "Out door" or selected_row["Type"] == "Outdoor" else 1)
                    new_cap = st.text_input("Capacity", value=selected_row["Capacity"])
                    new_status = st.selectbox("Status", ["Available", "Unavailable"], index=0 if selected_row["Status"] == "Available" else 1)
                with c2:
                    new_person = st.text_input("Contact Person", value=selected_row["Contact Person"])
                    new_phone = st.text_input("Phone", value=selected_row["Phone"])
                    new_addr = st.text_area("Address", value=selected_row["Address"], height=108)
                
                update_btn = st.form_submit_button("Save")
                
                if update_btn:
                    update_sql = """
                        UPDATE Location
                        SET loc_name=?,loc_type=?,loc_capacity=?,loc_status=?,
                            loc_contact_person=?, loc_phone=?, loc_address=?
                        WHERE location_id=?
                    """
                    final_type = new_type
                    params = (new_name, final_type, new_cap, new_status, new_person, new_phone, new_addr, current_id)
                    
                    if execute_update(update_sql,params):
                        st.success("Edited!")
                        st.rerun()
                
        with tab_delete:
            st.warning(f"Are you sure want to delete '{current_name}' ?")
            if st.button("Confirm", type="primary"):
                delete_sql = "DELETE FROM Location WHERE location_id = ?"
                if execute_update(delete_sql,(current_id,)):
                    st.success(f"Location: '{current_name}' Deletion successful")
                    st.rerun()
                    
    elif len(df) > 0:
        st.info("Select a row to view details, modify, or delete the location.")

except Exception as e:
    st.error(f"We got a error: {e}")