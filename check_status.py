import streamlit as st
import datetime
from utils import run_query

st.title("🎫 Event Status Checker")

col_tracker, col_details = st.columns([1, 2], gap="large")

with col_tracker:
    with st.container(border=True):
        st.subheader("🔍 Tracker")
        st.write("Enter your ID below:")
        with st.form("tracking_form"):
            event_id_str = st.text_input("Tracking ID", placeholder="e.g., 105")
            check_btn = st.form_submit_button("Track Event", type="primary", use_container_width=True)

with col_details:
    if check_btn:
        if not event_id_str.isdigit():
            st.warning("⚠️ Please enter a valid numeric Tracking ID.")
        else:
            event_id_input = int(event_id_str)
            with st.spinner("Searching database..."):
                sql = "SELECT evn_name, evn_status, evn_organizer, evn_start_date, evn_admin_comment, evn_image FROM Event WHERE event_id = ?"
                rows = run_query(sql, (event_id_input,))
            
            if rows:
                row = rows[0]
                name, status, organizer, s_date, admin_comment, img_data = row
                
                if isinstance(s_date, datetime.datetime):
                    date_display = s_date.strftime("%B %d, %Y at %I:%M %p")
                else:
                    date_display = str(s_date)
                
                with st.container(border=True):
                    col_head, col_status = st.columns([0.7, 0.3], gap="medium")
                    with col_head:
                        st.markdown(f"### {name}")
                    with col_status:
                        if status == "Approved": st.success("Approved", icon="✅")
                        elif status == "Declined": st.error("Declined", icon="❌")
                        else: st.warning("Pending", icon="⏳")

                    st.divider()
                    
                    c_date, c_org = st.columns(2)
                    with c_date:
                        st.markdown("**📅 Date & Time**")
                        st.write(date_display)
                    with c_org:
                        st.markdown("**👤 Organizer**")
                        st.write(organizer)
                    
                    if admin_comment and str(admin_comment).strip() != "":
                        st.write("") 
                        st.info(f"**Admin Note:** {admin_comment}", icon="📝")
                        
                    if img_data:
                        st.divider()
                        st.markdown("**🖼️ Event Poster**")
                        st.image(img_data, use_container_width=True)

            else:
                st.error(f"❌ No event found with ID **{event_id_input}**. Please verify your number.")
    else:
        st.info("👈 Use the tracker on the left to check your event status.")