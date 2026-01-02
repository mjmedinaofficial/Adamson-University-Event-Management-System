import streamlit as st
import pandas as pd
import datetime
import pyodbc

EVENT_COLORS = [
    "#3788d8", "#28a745", "#6f42c1", "#fd7e14", 
    "#e83e8c", "#d9534f", "#008b8b"
]

@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )

def run_query(query, params=None):
    conn = init_connection() 
    with conn.cursor() as cur:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()
         
def execute_update(query, params):
    conn = init_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False
    
def execute_insert(query, params):
    conn = init_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

def get_time_slots():
    times = []
    for h in range(24):
        for m in [0, 15, 30, 45]:
            t = datetime.time(h, m)
            times.append(t.strftime("%I:%M %p")) 
    return times

def check_conflict(location_id, start_dt, end_dt):
    conn = init_connection()
    sql = """
        SELECT COUNT(*) FROM Event 
        WHERE location_id = ? 
        AND evn_status != 'Declined'
        AND (evn_start_date < ? AND evn_end_date > ?)
    """
    with conn.cursor() as cur:
        cur.execute(sql, (location_id, end_dt, start_dt))
        count = cur.fetchone()[0]
    return count > 0

def check_login(username, password):
    conn = init_connection()
    sql = "SELECT count(*) FROM AdminUsers WHERE username=? AND password=?"
    with conn.cursor() as cur:
        cur.execute(sql, (username, password))
        return cur.fetchone()[0] > 0

def fetch_and_process_events_for_calendar():
    sql = """
        SELECT E.evn_name, E.evn_start_date, E.evn_end_date, L.loc_name, E.evn_description 
        FROM Event E
        LEFT JOIN Location L ON E.location_id = L.location_id
        WHERE E.evn_status = 'Approved'
    """
    rows = run_query(sql)
    
    events_raw = []
    unique_locations = set()
    
    for row in rows:
        name = row[0]
        start_val = row[1]
        end_val = row[2] if row[2] else start_val 
        loc_name = row[3] if row[3] else "Unknown"
        desc = row[4] if row[4] else ""
        
        dt_start, start = None, None
        if isinstance(start_val, datetime.datetime):
            dt_start = start_val
            start = start_val.date()
        elif isinstance(start_val, datetime.date):
            dt_start = datetime.datetime.combine(start_val, datetime.time(0,0))
            start = start_val
        else: continue
            
        dt_end, end = None, None
        if isinstance(end_val, datetime.datetime):
            dt_end = end_val
            end = end_val.date()
        elif isinstance(end_val, datetime.date):
            dt_end = datetime.datetime.combine(end_val, datetime.time(0,0))
            end = end_val
        else:
            dt_end = dt_start
            end = start
        
        events_raw.append({
            "name": name, "start": start, "end": end, "dt_start": dt_start,
            "dt_end": dt_end, "location": loc_name, "desc": desc,
            "duration": (end - start).days + 1
        })
        unique_locations.add(loc_name)
        
    sorted_locs = sorted(list(unique_locations))
    loc_color_map = {loc: EVENT_COLORS[i % len(EVENT_COLORS)] for i, loc in enumerate(sorted_locs)}
    
    day_slots = {} 
    events_raw.sort(key=lambda x: (x['start'], -x['duration']))
    
    for evt in events_raw:
        start_d = evt['start']
        duration = evt['duration']
        
        slot_index = 0
        while True:
            is_slot_free = True
            for i in range(duration):
                check_date = start_d + datetime.timedelta(days=i)
                if check_date not in day_slots:
                    day_slots[check_date] = {}
                if slot_index in day_slots[check_date]:
                    is_slot_free = False
                    break
            if is_slot_free:
                break
            else:
                slot_index += 1
        
        color = loc_color_map.get(evt['location'], "#555")
        
        for i in range(duration):
            current_d = start_d + datetime.timedelta(days=i)
            
            if duration == 1:
                pos_type = "evt-single"
                txt = evt['location']
            elif i == 0:
                pos_type = "evt-start"
                txt = evt['location']
            elif i == (duration - 1):
                pos_type = "evt-end"
                txt = "" 
            else:
                pos_type = "evt-mid"
                txt = "&nbsp;"
                
            day_slots[current_d][slot_index] = {
                "text": txt,
                "tooltip": f"{evt['name']} @ {evt['location']}",
                "color": color,
                "type": pos_type
            }
    
    return day_slots, loc_color_map, events_raw