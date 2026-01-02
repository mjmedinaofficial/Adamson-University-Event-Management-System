import streamlit as st
import datetime
from utils import run_query, execute_insert, get_time_slots, check_conflict

st.title("📝 Request a New Event")
st.markdown("Please fill out the details below. All events require **Admin Approval** before they are confirmed.")

with st.expander("ℹ️ Read: Guidelines for Approval", expanded=False):
    st.write("""
    1. **Lead Time:** Please submit requests at least 3 days in advance.
    2. **Locations:** Check location capacity before booking.
    3. **Organizer:** Ensure the contact name is accurate.
    """)

try:
    localtions_data = run_query("SELECT location_id, loc_name FROM Location WHERE loc_status != 'Unavailable'")
    location_options = {row[1]: row[0] for row in localtions_data}
except:
    location_options = {}

with st.container(border=True):
    with st.form("add_event_form"):
        st.subheader("Event Details")
        
        c1, c2 = st.columns(2)
        with c1:
            new_evn_name = st.text_input("Event Title", placeholder="e.g., Year End Party")
            new_evn_type = st.selectbox("Event Type", ["Public", "Private"])
        with c2:
            new_evn_organizer = st.text_input("Organizer Name", placeholder="Who is responsible?")
            selected_location_name = st.selectbox("Location", list(location_options.keys()))
        
        st.divider()
        st.caption("📅 Date & Time Schedule")

        time_options = get_time_slots() 
        idx_start = 32 if len(time_options) > 32 else 0
        idx_end = 68 if len(time_options) > 68 else 0

        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**Start**")
            start_d = st.date_input("Start Date", datetime.date.today())
            start_t_str = st.selectbox("Start Time", time_options, index=idx_start)
            
        with d2:
            st.markdown("**End**")
            end_d = st.date_input("End Date", datetime.date.today())
            end_t_str = st.selectbox("End Time", time_options, index=idx_end)

        new_evn_desc = st.text_area("Description / Purpose", placeholder="Describe the event activities...", height=100)
        
        st.markdown("---")
        uploaded_file = st.file_uploader("🖼️ Upload Event Poster (Optional)", type=['png', 'jpg', 'jpeg'])
        
        st.markdown("---")
        submit_btn = st.form_submit_button("🚀 Submit Request", type="primary", use_container_width=True)
    
        if submit_btn:
            if not new_evn_name or not selected_location_name:
                st.error("⚠️ Please fill in the Event Title and Location.")
            else:
                start_t = datetime.datetime.strptime(start_t_str, "%I:%M %p").time()
                end_t = datetime.datetime.strptime(end_t_str, "%I:%M %p").time()
                final_start_dt = datetime.datetime.combine(start_d, start_t)
                final_end_dt = datetime.datetime.combine(end_d, end_t)
                final_location_id = location_options[selected_location_name]

                if final_end_dt < final_start_dt:
                    st.error("⚠️ End Time cannot be before Start Time.")
                elif check_conflict(final_location_id, final_start_dt, final_end_dt):
                    st.error(f"❌ CONFLICT: '{selected_location_name}' is already booked for this time slot! Please choose another time or location.")
                else:
                    img_data = None
                    if uploaded_file is not None:
                        img_data = uploaded_file.read()

                    sql_query = """
                        INSERT INTO Event
                        (location_id, evn_name, evn_start_date, evn_end_date, 
                         evn_organizer, evn_description, evn_type, evn_status, evn_image)
                        OUTPUT INSERTED.event_id
                        VALUES (?,?,?,?,?,?,?,?,?)
                    """
                    params = (
                        final_location_id, new_evn_name, final_start_dt, final_end_dt,
                        new_evn_organizer, new_evn_desc, new_evn_type, 'Pending', img_data
                    )
                    
                    new_id = execute_insert(sql_query, params)
                    
                    if new_id:
                        st.balloons()
                        st.success("Request Submitted Successfully!")
                        
                        st.markdown(f"""
                        <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #c3e6cb;">
                            <h3 style="margin:0;">TRACKING ID</h3>
                            <h1 style="margin:0; font-size: 50px;">{new_id}</h1>
                            <p>Please save this number to check your status later.</p>
                        </div>
                        """, unsafe_allow_html=True)