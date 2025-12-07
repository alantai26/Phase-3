import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

# Example student data (replace this with an API call)
students = [
    {"ID": 1, "Name": "John P.", "Stage": "Interviewing", "Last Update": "Nov. 10, 2025"},
    {"ID": 2, "Name": "Smith L.", "Stage": "Offered", "Last Update": "Nov. 3, 2025"},
    {"ID": 3, "Name": "Dave E.", "Stage": "Applied", "Last Update": "July 4, 2020"},
]

df_students = pd.DataFrame(students)

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()
  
st.title('Career Coach Dashboard')

# Create tabs
tab1, tab2 = st.tabs(["Career Coach Dashboard", "Messages & Notifications"])

with tab1:
  st.subheader("Summary Metrics", divider="gray")
  col1, col2, col3 = st.columns(3)
  col1.write("Active Students: ")
  col2.write("Roles Secured: ")
  col3.write("In Progress: ")

  st.subheader("Student Activity", divider="gray")
  col_stage, col_sort, col_search, col_add, col_remove = st.columns(5)

  with col_stage:
    stage = st.selectbox(
      "Stage", 
      options=["All", "Applied", "Interviewing", "Offered", "Accepted", "Rejected"],
      index=1)
    
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
        st.info("Add Student functionality coming soon!")

  with col_remove:
    remove_student_id = st.text_input("Enter Student ID to Remove", key="remove_id")
    if st.button("Remove Student", use_container_width=True):
        st.info("Remove Student functionality coming soon!")

  # Apply filters
  filtered_students = df_students.copy()

  # Filter by stage

  # search by name

  # Sort by stage

  # display the table
  st.dataframe(filtered_students, use_container_width=True)

  st.subheader("Charts & Insights", divider="gray")
  col_pie, col_bar = st.columns(2)

  students = df_students.copy()

  # pie chart
  students['Role Secured'] = ['Intern', 'Intern', 'SWE']  # dummy values, will need to fix later
  
  stage_counts = students['Stage'].value_counts()
  fig1, ax1 = plt.subplots()
  ax1.pie(stage_counts, labels=stage_counts.index, autopct='%1.1f%%', startangle=90)
  ax1.set_title("Student Stage Distribution")
  col_pie.pyplot(fig1, use_container_width=True)

  # dummy data. need to get data from DB
  offers_data = [
    {"studentID": 888881, "dateApplied": "2025-01-10", "stage": "Offered"},
    {"studentID": 888882, "dateApplied": "2025-01-15", "stage": "Offered"},
    {"studentID": 888881, "dateApplied": "2025-02-20", "stage": "Offered"},
    {"studentID": 888882, "dateApplied": "2025-03-05", "stage": "Offered"},
    {"studentID": 888882, "dateApplied": "2025-03-20", "stage": "Offered"},
  ]

  offers_df = pd.DataFrame(offers_data)

  # Keep only 'Offered' stages
  offers_df = offers_df[offers_df['stage'] == 'Offered']

  # Convert dateApplied to datetime
  offers_df['dateApplied'] = pd.to_datetime(offers_df['dateApplied'])

  # Extract month number
  offers_df['month'] = offers_df['dateApplied'].dt.month

  # Group by month and count offers
  monthly_offers = offers_df.groupby('month').size().reindex(range(1, 13), fill_value=0)

  # Plot bar chart
  fig, ax = plt.subplots()
  months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  ax.bar(months, monthly_offers, color='skyblue')
  ax.set_title("Offers by Month")
  ax.set_ylabel("Number of Offers")
  ax.set_xlabel("Month")

  # Force y-axis to show only natural numbers
  ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

  col_bar.pyplot(fig, use_container_width=True)

with tab2:
  st.subheader("Notifications", divider="gray")

  st.subheader("Messages", divider="gray")