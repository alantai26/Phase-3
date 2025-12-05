import streamlit as st
import pandas as pd
import requests
import logging
logger = logging.getLogger(__name__)

from modules.nav import SideBarLinks



st.set_page_config(layout="wide", page_title="Appli-Tracker")
SideBarLinks()

if 'first_name' not in st.session_state:
    st.session_state['first_name'] = 'James'
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = 888881 

# Creating header
col_title, col_user = st.columns([4, 1])

with col_title:
    st.title("Appli-Tracker")

with col_user:
    st.write("")
    st.write("")
    st.write(f"**Logged In As:** {st.session_state['first_name']}")
    
    if st.button("Upload Resumes", type="secondary"):
        st.switch_page("pages/02_Upload_Page.py") 

col_sort, col_empty = st.columns([1, 4])
with col_sort:
    st.selectbox("Sort By", ["Date Added", "Company", "Status"])

try:
    api_url = f"http://web-api:4000/app_tracker/applications/{st.session_state['student_id']}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        df = pd.DataFrame()
        
except Exception as e:
    st.error(f"Error connecting to backend: {e}")
    df = pd.DataFrame()

# Creating Table
if not df.empty:
    if 'Status' in df.columns:
        df['Status_Normalized'] = df['Status'].str.lower()
    else:
        df['Status_Normalized'] = ''

    status_emoji_map = {
        "applied": "✅",
        "interviewing": "👀",
        "ghosted": "👻",
        "offer": "🎉",
        "rejected": "😢"
    }

    cols_to_keep = ['Company', 'Status_Icon', 'Resume_Used', 'Job_Board', 'App_Portal']
    cols_to_display = [c for c in cols_to_keep if c in df.columns]
    
    display_df = df[cols_to_display]

    # Displaying the table
    st.data_editor(
        display_df,
        column_config={
            "Company": st.column_config.TextColumn("Company"),
            "Status_Icon": st.column_config.TextColumn(
                "Status", 
                help="Current Status"
            ),
            "Resume_Used": st.column_config.SelectboxColumn(
                "Resume Used",
                width="medium",
                options=["Final Resume", "Updated Resume", "Software Engineer Focused"],
                required=True
            ),
            "Job_Board": st.column_config.TextColumn("Job Board"),
            "App_Portal": st.column_config.LinkColumn(
                "App Portal",
                display_text="View Portal"
            )
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )

    st.write("")

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
         if st.button("ADD MORE ➕", use_container_width=True):
             st.switch_page("pages/02_Job_Search.py")

    st.write("")

    # Key at the bottom
    st.markdown(
        "<div style='text-align: center; color: grey;'>"
        "Applied ✅ &nbsp;&nbsp; Interviewing 👀 &nbsp;&nbsp; Ghosted 👻 &nbsp;&nbsp; Offer 🎉 &nbsp;&nbsp; Rejected 😢"
        "</div>",
        unsafe_allow_html=True
    )

else:
    st.info("No applications found. Start tracking by clicking the Add More button!")