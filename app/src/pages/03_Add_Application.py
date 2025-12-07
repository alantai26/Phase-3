import streamlit as st
import requests
import time
from datetime import date
from modules.nav import SideBarLinks

# 1. Setup Page
st.set_page_config(layout="wide", page_title="Appli-Tracker - Add")
SideBarLinks()

# 2. Ensure Session State
if 'first_name' not in st.session_state:
    st.session_state['first_name'] = 'James'
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = 1 

# 3. Fetch Resumes (Required for the dropdown)
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
    st.error(f"Error fetching resumes: {e}")

if not resume_options:
    resume_options = ["No Resumes Found"]

st.title("Add New Job Application")
st.write(f"Enter details for **{st.session_state['first_name']}**'s new application.")

if st.button("← Back to Dashboard", type="secondary"):
    st.switch_page("pages/01_Application_Status.py")

st.markdown("---")

# Using a form to group inputs
with st.form("new_application_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        company = st.text_input("Company Name", placeholder="e.g. Netflix")
        position = st.text_input("Position", placeholder="e.g. Data Scientist")
        stage = st.selectbox("Stage", ["Applied", "Interviewing", "Ghosted", "Offer", "Rejected"])
    
    with col2:
        date_applied = st.date_input("Date Applied", value=date.today())
        
        # Resume Logic
        if resume_options:
            selected_label = st.selectbox("Resume Used", sorted(resume_options))
            selected_resume_id = resume_map.get(selected_label)
        else:
            st.warning("No resumes found.")
            selected_resume_id = None
            
        job_board = st.text_input("Job Board", placeholder="e.g. LinkedIn")

    st.write("")
    
    # Submit Button inside the form
    submit_button = st.form_submit_button("Submit Application", type="primary", use_container_width=True)

    if submit_button:
        if not company or not position:
            st.error("Please fill in Company and Position.")
        elif selected_resume_id is None:
            st.error("Please select a resume.")
        else:
            new_app_data = {
                "student_id": st.session_state['student_id'],
                "company": company,
                "position": position,
                "stage": stage,
                "date_applied": str(date_applied),
                "resume_id": selected_resume_id,
                "job_board": job_board
            }
            
            try:
                api_url = f"http://web-api:4000/app_tracker/applications/{st.session_state['student_id']}" 
                response = requests.post(api_url, json=new_app_data)
                
                if response.status_code == 201:
                    st.success(f"Application for {company} added successfully!")
                    time.sleep(1)
                    st.switch_page("pages/01_Application_Status.py")
                else:
                    st.error(f"Backend Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")