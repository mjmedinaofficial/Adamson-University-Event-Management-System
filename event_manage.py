import streamlit as st
import pandas as pd
import datetime
import io 
from utils import run_query, execute_update, get_time_slots

@st.dialog("Confirm Status Update")
def confirm_status_change(event_id, event_name, new_status):
    st.write(f"You are changing the status of:")
    st.subheader(f"📌 {event_name}")
    st.write(f"New Status: **{new_status}**")
    admin_note = st.text_area("Admin Comment (Optional)", placeholder="e.g., Approved, but please keep noise low.")
    st.divider()
    st.write("Are you sure you want to proceed?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Update", type="primary", use_container_width=True):
            sql = "UPDATE Event SET evn_status=?, evn_admin_comment=? WHERE event_id=?"
            if execute_update(sql, (new_status, admin_note, event_id)):
                st.success(f"Status updated to {new_status}"); st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True): st.rerun()

@st.dialog("Confirm Deletion")
def confirm_delete(event_id, event_name):
    st.warning("⚠️ DANGER ZONE")
    st.write(f"You are about to permanently delete: **{event_name}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete", type="primary", use_container_width=True):
            sql = "DELETE FROM Event WHERE event_id=?"; execute_update(sql, (event_id,)); st.success("Deleted."); st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True): st.rerun()

st.title("📊 Event Command Center")
st.write("Overview, approval, and management of campus events.")

try:
    fetch_sql = """
        SELECT E.event_id, E.evn_name, E.evn_type, E.evn_start_date, E.evn_end_date, 
               E.evn_organizer, E.evn_description, L.loc_name, E.evn_status, E.location_id, E.evn_image
        FROM Event E LEFT JOIN Location L ON E.location_id = L.location_id
    """
    rows = run_query(fetch_sql)
    columns = ["ID", "Name", "Type", "Start", "End", "Organizer", "Description", "Location", "Status", "Loc_ID", "Image"]
    df = pd.DataFrame.from_records(rows, columns=columns)
except Exception as e:
    st.error(f"Database Error: {e}"); df = pd.DataFrame()

col_metric, col_export = st.columns([3, 1])
with col_metric:
    if not df.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df))
        m2.metric("Pending", len(df[df["Status"]=="Pending"]))
        m3.metric("Approved", len(df[df["Status"]=="Approved"]))
        m4.metric("Declined", len(df[df["Status"]=="Declined"]))
with col_export:
    st.write("") 
    if not df.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Events')
        st.download_button("📥 Export Excel", data=buffer.getvalue(), file_name="events_report.xlsx", mime="application/vnd.ms-excel", use_container_width=True)

st.divider()

c_filter, c_search = st.columns([3, 2])
with c_filter:
    filter_status = st.radio("Filter by Status", ["All", "Pending", "Approved", "Declined"], horizontal=True, label_visibility="collapsed")
with c_search:
    search_term = st.text_input("🔍 Search Events", placeholder="Search by event name...", label_visibility="collapsed")

if not df.empty:
    if filter_status != "All": df = df[df["Status"] == filter_status]
    if search_term: df = df[df["Name"].str.contains(search_term, case=False, na=False)]

st.caption(f"Showing {len(df)} records")

event_table = st.dataframe(
    df, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun",
    column_config={
        "Loc_ID": None,
        "Image": None, 
        "Status": st.column_config.TextColumn("Status", validate="^(Pending|Approved|Declined)$"),
        "Start": st.column_config.DatetimeColumn("Start Date", format="MMM DD, YYYY h:mm a"),
        "End": st.column_config.DatetimeColumn("End Date", format="MMM DD, YYYY h:mm a")
    }
)

if len(event_table.selection.rows) > 0:
    selected_index = event_table.selection.rows[0]; selected_row = df.iloc[selected_index]
    current_id = int(selected_row["ID"]); current_name = selected_row["Name"]
    current_status = selected_row["Status"]; current_loc_id = selected_row["Loc_ID"]
    current_image = selected_row["Image"] 
    
    with st.container(border=True):
        st.subheader(f"⚙️ Managing: {current_name}")
        
        if current_image:
            st.markdown("**🖼️ Event Poster**")
            st.image(current_image, caption=f"Poster for {current_name}", use_container_width=True)
            st.divider()
        
        tab_approve, tab_edit, tab_delete = st.tabs(["🚦 Approval Status", "✏️ Edit Details", "🗑️ Delete"])
        
        with tab_approve:
            st.info(f"Current Status: **{current_status}**")
            b1, b2, b3 = st.columns(3)
            if b1.button("✅ Approve", use_container_width=True): confirm_status_change(current_id, current_name, "Approved")
            if b2.button("❌ Decline", use_container_width=True): confirm_status_change(current_id, current_name, "Declined")
            if b3.button("⏳ Reset", use_container_width=True): confirm_status_change(current_id, current_name, "Pending")

        with tab_edit:
            loc_rows = run_query("SELECT location_id, loc_name FROM Location")
            loc_map_id_to_name = {row[0]: row[1] for row in loc_rows}
            loc_map_name_to_id = {row[1]: row[0] for row in loc_rows}
            
            with st.form("edit_event_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Event Name", value=selected_row["Name"])
                    new_type = st.selectbox("Type", ["Public", "Private"], index=0 if selected_row["Type"]=="Public" else 1)
                    new_organizer = st.text_input("Organizer", value=selected_row["Organizer"])
                    
                    current_loc = loc_map_id_to_name.get(current_loc_id, None)
                    loc_list = list(loc_map_name_to_id.keys())
                    loc_idx = loc_list.index(current_loc) if current_loc in loc_list else 0
                    new_loc_name = st.selectbox("Location", loc_list, index=loc_idx)

                with c2:
                    curr_start = pd.to_datetime(selected_row["Start"]).to_pydatetime()
                    curr_end = pd.to_datetime(selected_row["End"]).to_pydatetime()
                    time_options = get_time_slots()
                    
                    try: s_idx = time_options.index(curr_start.strftime("%I:%M %p"))
                    except: s_idx = 0
                    try: e_idx = time_options.index(curr_end.strftime("%I:%M %p"))
                    except: e_idx = 0

                    c_sd, c_st = st.columns(2)
                    new_start_d = c_sd.date_input("Start Date", value=curr_start.date())
                    new_start_t_str = c_st.selectbox("Start Time", time_options, index=s_idx)
                    
                    c_ed, c_et = st.columns(2)
                    new_end_d = c_ed.date_input("End Date", value=curr_end.date())
                    new_end_t_str = c_et.selectbox("End Time", time_options, index=e_idx)
                    
                    new_desc = st.text_area("Description", value=selected_row["Description"], height=105)

                if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                    final_start = datetime.datetime.combine(new_start_d, datetime.datetime.strptime(new_start_t_str, "%I:%M %p").time())
                    final_end = datetime.datetime.combine(new_end_d, datetime.datetime.strptime(new_end_t_str, "%I:%M %p").time())
                    final_loc = loc_map_name_to_id[new_loc_name]
                    
                    sql = "UPDATE Event SET evn_name=?, evn_type=?, evn_organizer=?, evn_start_date=?, evn_end_date=?, evn_description=?, location_id=? WHERE event_id=?"
                    if execute_update(sql, (new_name, new_type, new_organizer, final_start, final_end, new_desc, final_loc, current_id)):
                        st.success("Updated!"); st.rerun()

        with tab_delete:
            st.error("Cannot be undone.")
            if st.button("🗑️ Delete Event", type="primary"): confirm_delete(current_id, current_name)

if not df.empty and len(event_table.selection.rows) == 0:
    st.info("Select an event row above to view details, update status, or edit information.")
elif df.empty:
    st.info("No events found in the database matching the current filter/search criteria.")