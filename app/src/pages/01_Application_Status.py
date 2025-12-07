import streamlit as st
import pandas as pd
import requests
import logging
import time
from datetime import date
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="Appli-Tracker")
SideBarLinks()

if 'first_name' not in st.session_state:
    st.session_state['first_name'] = 'James'
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = 1 

# Status Mapping
STATUS_DISPLAY_MAP = {
    "Applied": "✅",
    "Interviewing": "👀",
    "Ghosted": "👻",
    "Offer": "🎉",
    "Rejected": "😢"
}
STATUS_SAVE_MAP = {v: k.capitalize() for k, v in STATUS_DISPLAY_MAP.items()}

# Global Resume Fetch
resume_map = {} 
resume_options = []

try:
    api_url = f"http://web-api:4000/app_tracker/resumes/{st.session_state['student_id']}"
    response = requests.get(api_url)
    if response.status_code == 200:
        res_data = response.json()
        for r in res_data:
            resume_map[r['label']] = r['resumeID']
            resume_options.append(r['label'])
except Exception as e:
    logger.error(f"Error fetching resumes: {e}")

if not resume_options:
    resume_options = ["No Resumes Found"]

# Header
col_title, col_user = st.columns([4, 1])
with col_title:
    st.title("Appli-Tracker")
with col_user:
    st.write("")
    st.write(f"**Logged In As:** {st.session_state['first_name']}")
    if st.button("Upload Resumes", type="secondary"):
        st.switch_page("pages/02_Upload_Page.py") 

col_sort, col_empty = st.columns([1, 4])
with col_sort:
    sort_option = st.selectbox("Sort By", ["Date Added", "Company", "Status"])

# Fetch Data
try:
    api_url = f"http://web-api:4000/app_tracker/applications/{st.session_state['student_id']}?t={time.time()}"
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

# Callback Function (Update & Delete)
def save_changes():
    if "app_editor" in st.session_state:
        changes = st.session_state["app_editor"]["edited_rows"]
        
        for index, row_changes in changes.items():
            original_row = st.session_state['current_df'].iloc[index]
            app_id = int(original_row['applicationID'])
            
            if row_changes.get("Delete"):
                try:
                    del_url = f"http://web-api:4000/app_tracker/applications/{st.session_state['student_id']}/{app_id}"
                    response = requests.delete(del_url)
                    if response.status_code == 200:
                        st.toast(f"Deleted application for {original_row['Company']}", icon="🗑️")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Delete failed: {response.text}")
                except Exception as e:
                    st.error(f"Delete Error: {e}")
                continue

            # 2. UPDATE LOGIC
            display_status = row_changes.get("Status", original_row['Status'])
            clean_status = STATUS_SAVE_MAP.get(display_status, display_status)

            new_resume_label = row_changes.get("Resume_Used", original_row['Resume_Used'])
            resume_id_to_send = resume_map.get(new_resume_label, 199991) 

            payload = {
                "application_id": app_id,
                "company": row_changes.get("Company", original_row['Company']),
                "position": row_changes.get("Position", original_row['Position']),
                "stage": clean_status,
                "date_applied": str(row_changes.get("Date_Applied", original_row['Date_Applied'])),
                "resume_id": resume_id_to_send,
                "job_board": row_changes.get("Job_Board", original_row['Job_Board'])
            }
            
            try:
                put_url = f"http://web-api:4000/app_tracker/applications/{st.session_state['student_id']}"
                response = requests.put(put_url, json=payload)
                if response.status_code == 200:
                    st.toast(f"Updated {payload['company']}!", icon="✅")
                else:
                    st.error(f"Update failed: {response.text}")
            except Exception as e:
                st.error(f"Update Error: {e}")

# Display Table
if not df.empty:
    if 'Date_Applied' in df.columns:
        df['Date_Applied'] = pd.to_datetime(df['Date_Applied']).dt.date

    # Map Status text to Emojis for display
    if 'Status' in df.columns:
        df['Status'] = df['Status'].map(STATUS_DISPLAY_MAP).fillna(df['Status'])
        
    # Sorting
    if sort_option == "Date Added":
        df = df.sort_values(by="Date_Applied", ascending=False)
    elif sort_option == "Company":
        df = df.sort_values(by="Company", ascending=True)
    elif sort_option == "Status":
        df = df.sort_values(by="Status", ascending=True)

    # Add Delete Column
    df['Delete'] = False
    
    df = df.reset_index(drop=True)
    st.session_state['current_df'] = df

    cols_to_keep = ['Delete', 'applicationID', 'Date_Applied', 'Company', 'Position', 'Status', 'Resume_Used', 'Job_Board', 'App_Portal']
    cols_to_display = [c for c in cols_to_keep if c in df.columns]
    
    display_df = df[cols_to_display]

    st.data_editor(
        display_df,
        column_config={
            "Delete": st.column_config.CheckboxColumn(
                "🗑️?",
                width="small",
                default=False
            ),
            "applicationID": None,
            "Date_Applied": st.column_config.DateColumn("Date Applied", format="YYYY-MM-DD", required=True),
            "Company": st.column_config.TextColumn("Company", required=True),
            "Position": st.column_config.TextColumn("Position", required=True),
            
            "Status": st.column_config.SelectboxColumn(
                "Status",
                width="small",
                options=list(STATUS_DISPLAY_MAP.values())[:5], 
                required=True
            ),

            "Resume_Used": st.column_config.SelectboxColumn(
                "Resume Used",
                width="medium",
                options=resume_options,
                required=True
            ),
            "Job_Board": st.column_config.TextColumn("Job Board"),
            "App_Portal": st.column_config.LinkColumn("App Portal", display_text="View Portal"),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="app_editor",       
        on_change=save_changes 
    )

    st.write("")
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
         if st.button("ADD MORE ➕", use_container_width=True):
             st.switch_page("pages/03_Add_Application.py")

    st.markdown(
        "<div style='text-align: center; color: grey; margin-top: 20px;'>"
        "Applied ✅ &nbsp;&nbsp; Interviewing 👀 &nbsp;&nbsp; Ghosted 👻 &nbsp;&nbsp; Offer 🎉 &nbsp;&nbsp; Rejected 😢"
        "</div>",
        unsafe_allow_html=True
    )

else:
    st.info("No applications found. Start tracking by clicking the Add More button!")
    if st.button("ADD MORE ➕"):
        st.switch_page("pages/03_Add_Application.py")