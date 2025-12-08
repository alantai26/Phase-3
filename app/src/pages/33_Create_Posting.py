import streamlit as st
import requests
import time
from datetime import date
from modules.nav import SideBarLinks

st.set_page_config(layout="wide", page_title="Appli-Tracker - Add")
SideBarLinks()

st.title("Add New Job Posting")
st.write(f"Enter details for new job posting.")

if st.button("← Back to Dashboard", type="secondary"):
    st.switch_page("pages/31_Manage_Postings.py")

st.markdown("---")

# Using a form to group inputs
with st.form("new_posting_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Title", placeholder="e.g. Amazon Data Scientist Intern")
        roleType = st.text_input("Role", placeholder="e.g. Data Scientist")
        location = st.text_input("Location", placeholder="e.g. Remote, New York, NY")
    
    with col2:
        department = st.text_input("Department", placeholder="e.g. Engineering")
        datePosted = st.date_input("Date Posted", value=date.today())
        status = st.selectbox("Status", options=["Active", "Inactive"], index=0)
            
    st.write("")
    
    # Submit Button inside the form
    submit_button = st.form_submit_button("Submit Job Posting", type="primary", use_container_width=True)

    if submit_button:
        payload = {
        "title": title,
        "roleType": roleType,
        "location": location,
        "department": department,
        "status": status
    }
        coord_id = st.session_state.get("coordinator_id")
        url = f"http://web-api:4000/app_tracker/coordinator/{coord_id}/postings"
            
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                st.success("Job posting created successfully!")
                time.sleep(1)
                st.switch_page("pages/31_Manage_Postings.py")
            else:
                st.error(f"Backend Error: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")