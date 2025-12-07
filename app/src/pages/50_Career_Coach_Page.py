import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

coach_id = st.session_state.get('coach_id')

def get_coach_active_students(coach_id):
    API_URL = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/active_students"
    response = requests.get(API_URL)

    if response.status_code == 200:
        active_students = response.json()
        return active_students[0].get("Active_Students", 0)
    else:
        return 0

def get_coach_roles_secured(coach_id):
    API_URL = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/roles_secured"
    response = requests.get(API_URL)

    if response.status_code == 200:
        roles_secured = response.json()

        if roles_secured:
            return roles_secured[0].get("Roles_Secured", 0)
        else:
            return 0  # No roles secured
    else:
        st.error(f"Error fetching roles secured: {response.status_code}")
        return 0


def get_coach_in_progress(coach_id):
    API_URL = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/in_progress"
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        in_progress = response.json()
        if in_progress:
            return in_progress[0].get("In_Progress", 0)
        else:
            return 0  # No in progress students
    else:
        st.error(f"Error fetching in progress students: {response.status_code}")
        return 0
    
def get_student_activity(coach_id):
    url = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/student_activity"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error(f"Failed to fetch student activity: {response.status_code}")
        return pd.DataFrame()
    
def get_student_applications(coach_id):
    url = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/student_applications"
    r = requests.get(url)
    if r.status_code == 200:
        return pd.DataFrame(r.json())
    else:
        st.error("Failed to fetch student application data.")
        return pd.DataFrame()

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()
  
st.title('Career Coach Dashboard')

# Create tabs
tab1, = st.tabs(["Career Coach Dashboard"])

with tab1:
  # ==============================================
  # Summary Metrics
  # ==============================================
  st.subheader("Summary Metrics", divider="gray")
  col1, col2, col3 = st.columns(3)

  r1 = get_coach_active_students(coach_id)
  r2 = get_coach_roles_secured(coach_id)
  r3 = get_coach_in_progress(coach_id)

  col1.write(f"Active Students: {r1}")
  col2.write(f"Roles Secured: {r2}")
  col3.write(f"In Progress: {r3}")


  # ==============================================
  # Student Activity Table with Filters
  # ==============================================

  st.subheader("Student Activity", divider="gray")
  col_stage, col_sort, col_search, col_add, col_remove = st.columns(5)

  with col_stage:
    stage = st.selectbox(
      "Stage", 
      options=["All", "Applied", "Interviewing", "Offered", "Accepted", "Rejected"],
      index=0)
    
  with col_sort:
    sort_by = st.selectbox(
      "Sort By", 
      options=["Applied", "Interviewing", "Offered"],
      index=1)
  
  with col_search:
    search_term = st.text_input("Search (enter name)")

  with col_add:
    add_student_id = st.text_input("Enter Student ID to Add", key="add_id")
    if st.button("Add Student", use_container_width=True):  
        if add_student_id.strip():
            API_URL = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/add_student"
            payload = {"student_id": int(add_student_id)}
            r = requests.post(API_URL, json=payload)
            if r.status_code == 200:
                st.success(f"Student {add_student_id} added successfully!")
            else:
                st.error(f"Failed to add student: {r.text}")
        else:
            st.warning("Please enter a Student ID to add.")

  with col_remove:
    remove_student_id = st.text_input("Enter Student ID to Remove", key="remove_id")
    if st.button("Remove Student", use_container_width=True):
        if remove_student_id.strip().isdigit():
            student_id = int(remove_student_id)
            API_URL = f"http://web-api:4000/app_tracker/career_coach/{coach_id}/remove_student/{student_id}"
            response = requests.put(API_URL)

            if response.status_code == 200:
                st.success(f"Student {student_id} successfully removed from your coaching list.")
            else:
                st.error(f"Failed to remove student: {response.json().get('message', response.text)}")
        else:
            st.warning("Please enter a valid student ID.")

  df = get_student_activity(coach_id)

  # Filter by stage (case-insensitive)
  if stage != "All":
      df = df[df['Stage'].str.lower() == stage.lower()]

  # Search by name
  if search_term.strip():
      df = df[df["Name"].str.contains(search_term, case=False, na=False)]

  # Sort by stage if selected
  if sort_by:
      df = df.sort_values(by="Stage")

  # display the table
  st.dataframe(df, use_container_width=True)


  # ==============================================
  # Charts & Insights
  # ==============================================

  st.subheader("Charts & Insights", divider="gray")
  col_pie, col_bar = st.columns(2)
  
  applications_df = get_student_applications(coach_id)

  # Remove rows where student has no job applications
  applications_df = applications_df[applications_df['applicationID'].notna()]

  if not applications_df.empty:

  # ==============================================
  # Pie Chart
  # ==============================================

    # Create normalized category column
    applications_df['stage_category'] = applications_df['stage'].str.lower().map({
        # Applied
        "applied": "Applied",
        "application submitted": "Applied",

        # Interviewing
        "interviewing": "Interviewing",
        "phone screen": "Interviewing",
        "technical interview": "Interviewing",
        "onsite": "Interviewing",
        "behavioral interview": "Interviewing",

        # Offered
        "offered": "Offered",
        "offer": "Offered"
    })

    # Count the 3 major groups
    stage_counts = applications_df['stage_category'].value_counts()

    # Generate pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(stage_counts, labels=stage_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title("Student Activity Distribution")

    col_pie.pyplot(fig1, use_container_width=True)


  # ==============================================
  # Bar Chart 
  # ==============================================

    # Keep only "Offered"
    offers_df = applications_df[applications_df['stage_category'] == "Offered"].copy()

    # Convert to datetime
    offers_df['dateApplied'] = pd.to_datetime(offers_df['dateApplied'])

    # Extract month (1–12)
    offers_df['month'] = offers_df['dateApplied'].dt.month

    # Count offers per month, ensure all months exist
    monthly_offers = offers_df.groupby('month').size().reindex(range(1, 13), fill_value=0)

    # Bar chart
    fig, ax = plt.subplots()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    ax.bar(months, monthly_offers)
    ax.set_title("Offers by Month")
    ax.set_ylabel("Number of Offers")
    ax.set_xlabel("Month")
    
    max_val = monthly_offers.max()

    if max_val == 0:
        ax.set_ylim(0, 3)
    else:
        ax.set_ylim(0, max_val + 1)

    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))

    col_bar.pyplot(fig, use_container_width=True)

  else:
    col_pie.write("No application data available for pie chart.")
    col_bar.write("No application data available for bar chart.")