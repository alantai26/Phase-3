import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()
  
st.title('Job Postings Management')

# Example dynamic values
posting_title = "Software Engineer Intern"
expires_on = "2025-01-10"

col1, col2 = st.columns([3, 1])


col1.write(f"**Posting expiring soon:** {posting_title} (expires {expires_on})")

# Column 2: Button
if col2.button("Manage", key="manage_posting"):
    st.write("Manage button clicked!")   # (Add functionality later) !!!!!!!!!!!!!!

status1, platforms1, sort1 = st.columns(3)

with status1:
    status = st.selectbox(
      "Status", 
      options=["All", "Active", "Expired", "Paused", "Up", "Down"],
      index=0)
    
with platforms1:
    platforms = st.multiselect(
      "Platforms", 
      options=["LinkedIn", "Indeed", "Handshake", "Company Website", "NUworks"],
      default=[])

with sort1:
    sort = st.selectbox(
      "Sort by",
      options=["Title", "Status", "Applicants"],
      index=0)
    

# Get real data from API in future !!!!!!!!!!!!!!
data = {
    "Title": ["Software Engineer Intern", "Data Analyst", "Marketing Coordinator",
              "Backend Engineer", "Product Manager"],
    "Status": ["Active", "Expired", "Active", "Paused", "Active"],
    "Applicants": [53, 12, 88, 21, 33],
    "Platform": ["LinkedIn", "Indeed", "Handshake", "Company Website", "NUworks"]
}

df = pd.DataFrame(data)

# Status filter
if status != "All":
    df = df[df["Status"] == status]

# Platform filter
if platforms:
    df = df[df["Platform"].isin(platforms)]

# Sorting
df = df.sort_values(by=sort)

# apply filters and sort
# display table

st.subheader("Job Postings Table", divider="gray")
st.dataframe(df, use_container_width=True)