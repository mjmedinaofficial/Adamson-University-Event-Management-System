import streamlit as st
import calendar
import datetime
from utils import run_query
from utils import fetch_and_process_events_for_calendar, EVENT_COLORS

@st.dialog("Event Details")
def show_event_details(event_name, location, start_dt, end_dt, description):
    st.markdown(f"### {event_name}")
    st.caption(f"📍 {location}")
    st.markdown("---")
    
    start_str = start_dt.strftime('%b %d, %Y at %I:%M %p')
    end_str = end_dt.strftime('%b %d, %Y at %I:%M %p')

    st.markdown(f"**Start:** {start_str}")
    st.caption(f"**End:** {end_str}") 
    
    st.markdown("---")
    st.markdown("**Description / Purpose**")
    if description:
        st.markdown(description)
    else:
        st.info("No description provided.")
    
    if st.button("Close", type="primary"):
        st.rerun()

sidebar_state = "expanded" 

st.set_page_config(
    page_title="Campus Event Portal", 
    page_icon="📅", 
    layout="wide", 
    initial_sidebar_state=sidebar_state 
)

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; margin-top: 0rem; }
        ::-webkit-scrollbar { width: 12px; height: 12px; }
        ::-webkit-scrollbar-track { background: #0e1117; }
        ::-webkit-scrollbar-thumb { background: #555; border-radius: 6px; border: 2px solid #0e1117; }
        html { scrollbar-width: thin; scrollbar-color: #555 #0e1117; }
        
        .st-emotion-cache-1cypcdb { padding-left: 0rem !important; padding-right: 0rem !important; }

        .sidebar-cal-td { 
            height: 35px; 
            width: 14.28%; 
            vertical-align: top; 
            border: 1px solid #444; 
            padding: 0px !important; 
            background-color: #262730; 
            overflow: hidden;
            box-sizing: border-box !important; 
        }
        .sidebar-cal-day { font-weight: bold; font-size: 10px; padding: 1px 2px; color: #fff; display: block; text-align: right; line-height: 1; }
        .sidebar-cal-event { height: 10px; font-size: 0px; color: white; padding: 0px; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; cursor: pointer; line-height: 1; font-weight: 500; }
        .sidebar-cal-spacer { height: 10px; margin-bottom: 0px; display: block; background-color: transparent; }
        .evt-start { margin-right: -1px; border-radius: 3px 0 0 3px; }
        .evt-mid { margin-left: -1px; margin-right: -1px; border-radius: 0; }
        .evt-end { margin-left: -1px; border-radius: 0 3px 3px 0; }
        .evt-single { border-radius: 3px; margin-left: 1px; margin-right: 1px; }
        .cal-empty { background-color: #0e1117; border: none; }
        .sidebar-cal-th { color: #fff !important; }
    </style>
""", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.session_state.role = None
if "cal_year" not in st.session_state:
    st.session_state.cal_year = datetime.date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = datetime.date.today().month

def logout():
    st.session_state.role = None
    st.rerun()

def change_month(amount):
    new_month = st.session_state.cal_month + amount
    if new_month > 12:
        st.session_state.cal_month = 1; st.session_state.cal_year += 1
    elif new_month < 1:
        st.session_state.cal_month = 12; st.session_state.cal_year -= 1
    else:
        st.session_state.cal_month = new_month
        st.rerun() 

def render_sidebar_content():
    cal_year = st.session_state.cal_year
    cal_month = st.session_state.cal_month
    
    try:
        day_slots, loc_color_map, events_raw = fetch_and_process_events_for_calendar()
    except Exception:
        day_slots = {}; events_raw = []; loc_color_map = {}
        
    today = datetime.date.today()
    events_raw.sort(key=lambda x: x['start'])
    upcoming_events = [e for e in events_raw if e['end'] >= today]
    past_events = [e for e in events_raw if e['end'] < today]
    past_events.sort(key=lambda x: x['start'], reverse=True)

    st.markdown("### 🗓️ Quick View Calendar")
    col_title = st.columns([1])[0] 
    with col_title:
        st.markdown(f"### <div style='text-align: left; margin: 0;'>{calendar.month_name[cal_month]} {cal_year}</div>", unsafe_allow_html=True)

    st.markdown("<style>.sidebar-cal-table { width: 100%; table-layout: fixed; border-collapse: collapse; margin: 0px;} .sidebar-cal-th { text-align: center; padding: 2px; font-size: 10px; } .sidebar-cal-empty { background-color: #0e1117; border: none; }</style>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(cal_year, cal_month)
    html = "<table class='sidebar-cal-table'><thead><tr>"
    for day in ["M", "T", "W", "T", "F", "S", "S"]: html += f"<th class='sidebar-cal-th'>{day}</th>"
    html += "</tr></thead><tbody>"

    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0: html += "<td class='sidebar-cal-td sidebar-cal-empty'></td>"
            else:
                current_date = datetime.date(cal_year, cal_month, day)
                html += f"<td class='sidebar-cal-td'><span class='sidebar-cal-day'>{day}</span>"
                if current_date in day_slots:
                    for i in range(2):
                        if i in day_slots[current_date]:
                            evt = day_slots[current_date][i]
                            html += f"<div class='sidebar-cal-event {evt['type']}' style='background-color: {evt['color']};' title='{evt['tooltip']}'></div>"
                        else: html += "<div class='sidebar-cal-spacer'></div>"
                html += "</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)
    st.caption("Each colored line represents an approved event.")
    
    st.markdown("---") 
    st.markdown("### ✨ Quick View Events")
    
    st.markdown(f"**Upcoming Events ({len(upcoming_events)})**")
    with st.container(border=True):
        if upcoming_events:
            for event in upcoming_events[:3]: 
                event_key = f"upcoming_{event['name']}_{event['start']}"
                st.markdown(f"**{event['name']}**")
                st.caption(f"📅 {event['start'].strftime('%b %d')} @ {event['location']}")
                if st.button("Details", key=event_key, use_container_width=True):
                    show_event_details(event['name'], event['location'], event['dt_start'], event['dt_end'], event['desc'])
            if len(upcoming_events) > 3: st.caption(f"... and {len(upcoming_events) - 3} more.")
        else: st.info("No upcoming events scheduled.")
            
    st.markdown(f"**Past Events ({len(past_events)})**")
    with st.container(border=True):
        if past_events:
            for event in past_events[:3]:
                event_key = f"past_{event['name']}_{event['start']}"
                st.markdown(f"**{event['name']}**")
                st.caption(f"✅ Ended {event['end'].strftime('%b %d')} @ {event['location']}")
                if st.button("Details", key=event_key, use_container_width=True):
                    show_event_details(event['name'], event['location'], event['dt_start'], event['dt_end'], event['desc'])
        else: st.info("No past events found.")


def landing_page():
    with st.sidebar:
        render_sidebar_content()

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    
    try:
        st.image("1.png", use_container_width=True)
    except:
        st.write("") 
        
    st.markdown("<h1 style='text-align: center;'>📅 Campus Event Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Plan, Organize, and Celebrate.</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 10, 1]) 
    with col2:
        c1, c2 = st.columns(2, gap="large")

        with c1:
            with st.container(border=True):
                st.subheader("🙋 For Students")
                st.write("Access public events and proposals.")
                st.write("") 
                
                if st.button("📅 View Event Calendar", use_container_width=True):
                    st.session_state.role = "view_calendar"
                    st.rerun()
                
                if st.button("✨ Create New Event", type="primary", use_container_width=True):
                    st.session_state.role = "student_create"
                    st.rerun()
                
                if st.button("🔍 Check Approval Status", use_container_width=True):
                    st.session_state.role = "student_check"
                    st.rerun()

        with c2:
            with st.container(border=True):
                st.subheader("🛡️ Admin Portal")
                st.write("Manage requests & locations.")
                
                with st.form("admin_login"):
                    user_input = st.text_input("Username", placeholder="e.g., admin")
                    pass_input = st.text_input("Password", type="password", placeholder="Key...")
                    st.write("")
                    submit = st.form_submit_button("🔐 Login", use_container_width=True)
                    
                    if submit:
                        from utils import check_login
                        if check_login(user_input, pass_input): 
                            st.session_state.role = "admin"
                            st.rerun()
                        else:
                            st.error("Invalid Username or Password.")


pages = {}

if st.session_state.role is None:
    pages["Portal"] = [st.Page(landing_page, title="Home", icon="🏠")]

elif st.session_state.role == "view_calendar":
    pages["Public"] = [st.Page("view_calendar.py", title="🗓️ Event Calendar")]

elif st.session_state.role == "student_create":
    pages["Student Actions"] = [st.Page("add_event.py", title="📝 Request Event")]

elif st.session_state.role == "student_check":
    pages["Student Actions"] = [st.Page("check_status.py", title="🎫 Check Status")]

elif st.session_state.role == "admin":
    pages["Management"] = [
        st.Page("summary.py", title="📈 Analytics Summary"),
        st.Page("event_manage.py", title="📊 Event Management"),
        st.Page("location_list.py", title="📍 Locations"),
        st.Page("add_location.py", title="➕ Add Location"),
    ]

pg = st.navigation(pages)

with st.sidebar:
    if st.session_state.role is not None:
        if st.session_state.role == "admin":
            st.write(f"Logged in as: **{st.session_state.role.replace('_', ' ').title()}**")
        
        if st.button("🚪 Logout / Main Menu", use_container_width=True):
            logout()

pg.run()