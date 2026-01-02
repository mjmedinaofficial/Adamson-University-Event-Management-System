import streamlit as st
import calendar
import datetime
from utils import run_query, fetch_and_process_events_for_calendar, EVENT_COLORS

st.title("🗓️ Campus Event Calendar")

if "cal_year" not in st.session_state:
    st.session_state.cal_year = datetime.date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = datetime.date.today().month

def change_month(amount):
    new_month = st.session_state.cal_month + amount
    if new_month > 12:
        st.session_state.cal_month = 1
        st.session_state.cal_year += 1
    elif new_month < 1:
        st.session_state.cal_month = 12
        st.session_state.cal_year -= 1
    else:
        st.session_state.cal_month = new_month

year = st.session_state.cal_year
month = st.session_state.cal_month
month_name = calendar.month_name[month]

left_buff, col_prev, col_title, col_next, right_buff = st.columns([2, 1.2, 4, 1.2, 2])

with col_prev:
    st.write("") 
    st.write("") 
    if st.button("⬅️ Prev", use_container_width=True): 
        change_month(-1)
        st.rerun()

with col_title:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <h2 style="margin-bottom: 0px; padding-bottom: 0px;">{month_name}</h2>
            <p style="font-size: 18px; color: gray; margin-top: -5px;">{year}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_next:
    st.write("") 
    st.write("") 
    if st.button("Next ➡️", use_container_width=True):
        change_month(1)
        st.rerun()

st.markdown("""
    <style>
        .cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
        .cal-th { 
            text-align: center; color: #888; padding: 5px; 
            font-size: 12px; border-bottom: 1px solid #444; 
        }
        .cal-td { 
            height: 75px; 
            width: 14.28%; 
            vertical-align: top; 
            border: 1px solid #444; 
            padding: 0px !important; 
            background-color: #262730;
            overflow: hidden;
        }
        .cal-day { 
            font-weight: bold; 
            font-size: 11px; 
            padding: 2px 4px;
            color: #aaa; 
            display: block; 
            text-align: right;
        }
        .cal-event { 
            height: 16px;
            font-size: 9px;
            color: white; 
            padding: 1px 4px; 
            margin-bottom: 1px;
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
            display: block;
            cursor: pointer;
            line-height: 1.5;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.6);
            font-weight: 500;
        }
        .cal-spacer { height: 16px; margin-bottom: 1px; display: block; background-color: transparent; }
        .evt-start { margin-right: -1px; border-radius: 3px 0 0 3px; }
        .evt-mid { margin-left: -1px; margin-right: -1px; border-radius: 0; }
        .evt-end { margin-left: -1px; border-radius: 0 3px 3px 0; }
        .evt-single { border-radius: 3px; margin-left: 1px; margin-right: 1px; }
        .cal-empty { background-color: #0e1117; border: none; }
    </style>
""", unsafe_allow_html=True)

try:
    day_slots, loc_color_map, events_raw = fetch_and_process_events_for_calendar()
except Exception as e:
    st.error(f"Error: {e}")
    day_slots = {}
    events_raw = []
    loc_color_map = {}

cal = calendar.monthcalendar(year, month)

col_cal, col_details = st.columns([3, 1], gap="large")

with col_cal:
    legend_html = "<div style='margin-bottom: 5px; font-size: 11px;'>"
    for loc, col in loc_color_map.items():
        legend_html += f"<span style='margin-right:10px;'><span style='color:{col};'>●</span> {loc}</span>"
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)

    html = "<table class='cal-table'><thead><tr>"
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        html += f"<th class='cal-th'>{day}</th>"
    html += "</tr></thead><tbody>"

    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td class='cal-td cal-empty'></td>"
            else:
                current_date = datetime.date(year, month, day)
                html += f"<td class='cal-td'>"
                html += f"<span class='cal-day'>{day}</span>"
                if current_date in day_slots:
                    slots_for_today = day_slots[current_date]
                    max_slot = max(slots_for_today.keys()) if slots_for_today else -1
                    for i in range(max_slot + 1):
                        if i in slots_for_today:
                            evt = slots_for_today[i]
                            style = f"background-color: {evt['color']};"
                            html += f"<div class='cal-event {evt['type']}' style='{style}' title='{evt['tooltip']}'>{evt['text']}</div>"
                        else:
                            html += "<div class='cal-spacer'></div>"
                html += "</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

with col_details:
    st.subheader("📌 Details")
    st.divider()
    
    current_month_events = [e for e in events_raw if e['start'].month == month and e['start'].year == year]
    current_month_events.sort(key=lambda x: x['start'])
    
    if current_month_events:
        for event in current_month_events:
            color = loc_color_map.get(event['location'], "#555")
            with st.container(border=True):
                s_str = event['dt_start'].strftime('%b %d, %I:%M %p')
                e_str = event['dt_end'].strftime('%b %d, %I:%M %p')
                if event['start'] == event['end']:
                    d_str = f"{s_str} - {event['dt_end'].strftime('%I:%M %p')}"
                else:
                    d_str = f"{s_str} - <br>{e_str}"
                st.markdown(
                    f"<div style='border-left: 4px solid {color}; padding-left: 8px;'>"
                    f"<small>{d_str}</small><br>"
                    f"<b>{event['name']}</b>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                st.caption(f"📍 {event['location']}")
    else:
        st.info(f"No events for {month_name}.")