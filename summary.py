import streamlit as st
import pandas as pd
import plotly.express as px
from utils import run_query 

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #001f3f, #4da6ff) !important; 
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }

    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }

    [data-testid="stMetricLabel"] {
        color: #e0e0e0 !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stMetricDelta"] {
        position: absolute;
        bottom: 14px; 
        right: 14px; 
        color: #66BB6A !important; 
        font-size: 0.9em;
        font-weight: 600;
    }
    
    div[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
        position: relative; 
        min-height: 100px; 
    }

    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        padding: 5px;
    }
    [data-testid="stDataFrame"] * {
        color: black !important;
    }

    h1, h2, h3, h4, h5, h6, .stMarkdown, p {
        color: #ffffff !important;
    }
    
    hr {
        border: 0;
        height: 2px;
        background: rgba(255, 255, 255, 0.25);
        margin: 25px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col_logo, col_text, col_placeholder = st.columns([1, 4, 1])

with col_text:
    banner_html = """
    <div class='au-banner-container'>
        <div class='au-banner-text'>
            <span class='gradient-text'>ADAMSON UNIVERSITY</span>
            <span class='shadow-text'> EVENTS</span>
        </div>
        <div class='banner-subtitle'>Management Analytics</div>
    </div>

    <style>
    .au-banner-container {
        background: linear-gradient(90deg, #001f3f, #4da6ff); 
        border-radius: 20px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.7); 
        padding: 25px 0;
        margin-bottom: 30px;
        text-align: center;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .gradient-text {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(270deg, #ff512f, #dd2476, #1fa2ff, #12d8fa);
        background-size: 800% 800%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientMove 8s ease infinite;
    }

    .shadow-text {
        font-size: 3rem;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 10px #fff, 0 0 20px #12d8fa, 0 0 30px #1fa2ff;
        margin-left: 10px;
    }

    .banner-subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: #e0f7fa;
        margin-top: 5px;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
    }

    @keyframes gradientMove {
        0%{background-position:0% 50%;}
        50%{background-position:100% 50%;}
        100%{background-position:0% 50%;}
    }

    .au-banner-container::after {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 1%, transparent 1%);
        background-size: 20px 20px;
        animation: floatStripes 20s linear infinite;
        pointer-events: none;
    }

    @keyframes floatStripes {
        0% { transform: rotate(0deg) translateY(0px);}
        50% { transform: rotate(180deg) translateY(50px);}
        100% { transform: rotate(360deg) translateY(0px);}
    }
    </style>
    """
    st.markdown(banner_html, unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    st.markdown("Use this panel for navigation and quick filtering.")
    st.markdown("---")
    st.subheader("Database Status")
    st.success("✅ Connection: Active")

st.markdown("## 🗓️ Analytics Overview")
st.caption("Real-time summary of event requests and approvals.")
st.markdown("---")

with st.container():
    st.markdown("### 📈 Status Breakdown")
    
    try:
        fetch_summary_sql = """
            SELECT 
                COUNT(*) as Total_Event,
                SUM(CASE WHEN evn_start_date BETWEEN GETDATE() AND DATEADD(day, 7, GETDATE()) THEN 1 ELSE 0 END) as Soon_Event,
                SUM(CASE WHEN evn_status = 'Pending' THEN 1 ELSE 0 END) as Preparing,
                SUM(CASE WHEN evn_status = 'Approved' THEN 1 ELSE 0 END) as Completed,
                SUM(CASE WHEN evn_status = 'Declined' THEN 1 ELSE 0 END) as Canceled
            FROM Event;
        """

        event_summary = run_query(fetch_summary_sql)
        columns = ["Total_Event", "Soon_Event", "Preparing", "Completed", "Canceled"]

        if event_summary:
            df_summary = pd.DataFrame.from_records(event_summary, columns=columns).fillna(0)
            row = df_summary.iloc[0]

            cols = st.columns(5, gap="medium")
            
            metric_titles = ["Total Events 📚", "Next 7 Days 🚀", "Pending 📝", "Approved 🎉", "Declined 🚫"]
            metric_values = [
                int(row["Total_Event"]),
                int(row["Soon_Event"]),
                int(row["Preparing"]),
                int(row["Completed"]),
                int(row["Canceled"])
            ]
            metric_deltas = [
                None,
                f"{int(row['Soon_Event'])} in next week",
                None,
                None,
                None
            ]

            for i in range(5):
                with cols[i]:
                    st.metric(
                        label=metric_titles[i],
                        value=metric_values[i],
                        delta=metric_deltas[i] if metric_deltas[i] else None,
                        delta_color="normal"
                    )

            st.markdown("<hr>", unsafe_allow_html=True)
            
            col_chart, col_empty = st.columns([2, 1])
            with col_chart:
                st.markdown("### 📊 Event Distribution")
                chart_data = {
                    'Status': ['Preparing (Pending)', 'Completed (Approved)', 'Canceled (Declined)'],
                    'Count': [int(row["Preparing"]), int(row["Completed"]), int(row["Canceled"])]
                }
                df_chart = pd.DataFrame(chart_data)
                df_chart = df_chart[df_chart['Count'] > 0]

                if not df_chart.empty:
                    fig = px.pie(
                        df_chart,
                        values='Count',
                        names='Status',
                        hole=0.4,
                        color='Status',
                        color_discrete_map={
                            'Preparing (Pending)':'#FFA726', 
                            'Completed (Approved)':'#66BB6A', 
                            'Canceled (Declined)':'#EF5350'
                        }
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        showlegend=True, 
                        margin=dict(l=20, r=20, t=30, b=20), 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    ) 
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data to generate chart.")
        else:
            st.warning("⚠️ No data found in the Event table.")

    except Exception as e:
        st.error(f"❌ Database Error: **{e}**")

st.markdown("<hr>", unsafe_allow_html=True)

with st.container():
    st.markdown("### 📑 Recent & Upcoming Log")
    
    try:
        fetch_details_sql = """
            SELECT TOP 20
                evn_name,
                FORMAT(evn_start_date, 'yyyy-MM-dd') as Start_Date,
                FORMAT(evn_end_date, 'yyyy-MM-dd') as End_Date,
                evn_status
            FROM Event
            ORDER BY evn_start_date DESC;
        """
        
        event_details = run_query(fetch_details_sql)
        detail_columns = ["Event Name", "Start Date", "End Date", "Status"]

        if event_details:
            df_details = pd.DataFrame.from_records(event_details, columns=detail_columns)

            st.dataframe(
                df_details,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Event Name": st.column_config.TextColumn("Event Name"),
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
            )
        else:
            st.info("ℹ️ No events found.")
            
    except Exception as e:
        st.error(f"Database Error: {e}")