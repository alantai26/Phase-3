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

coord_id = st.session_state.get('coordinator_id')


def get_soonest_expiring_listing(coordinator_id, days=7):
    url = f"http://web-api:4000/app_tracker/coordinator/{coordinator_id}/expiring-listings"
    params = {"days": days}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error("Failed to load expiring listing.")
        return None

    data = response.json()
    if len(data) == 0:
        return None
    
    return data[0]

def get_postings_with_platforms(coordinator_id):
    # Get postings
    postings_url = f"http://web-api:4000/app_tracker/coordinator/{coordinator_id}/postings"
    r_postings = requests.get(postings_url)
    if r_postings.status_code != 200:
        st.error("Failed to load postings.")
        return pd.DataFrame()

    postings_df = pd.DataFrame(r_postings.json())
    if postings_df.empty:
        return pd.DataFrame()

    # Get listings/platforms for postings
    listings_url = f"http://web-api:4000/app_tracker/coordinator/{coordinator_id}/listings"
    r_listings = requests.get(listings_url)
    if r_listings.status_code != 200:
      st.error("Failed to load listings.")
      return postings_df

    listings_df = pd.DataFrame(r_listings.json())
    if listings_df.empty:
        postings_df["platform"] = ""
        return postings_df

    # merge postings with platforms
    # some postings may have multiple listings/platforms, so join and aggregate
    platform_df = listings_df.groupby("postingID")["platform"].apply(lambda x: ", ".join(sorted(x.dropna().unique()))).reset_index()

    merged_df = pd.merge(
        postings_df,
        platform_df,
        how="left",
        on="postingID"
    )

    # fill missing platforms with empty string
    merged_df["platform"] = merged_df["platform"].fillna("")

    return merged_df

# ============
# Top Row: Expiring Listing + Add Posting Button
# ============
col1, col2 = st.columns([3, 1])

# Column 1: Expiring Listing
listing = get_soonest_expiring_listing(coord_id)

if listing:
    posting_title = listing['title']
    expires_on = listing['expiresOn']
    col1.write(f"Posting expiring soon: {posting_title} (expires {expires_on})")
else:
    col1.write("No postings expiring soon.")

# Column 2: Button
if col2.button("Add Posting"):
    st.switch_page("pages/33_Create_Posting.py")


# ============
# Filters Row
# ============
status1, platforms1, sort1 = st.columns(3)

with status1:
    status = st.selectbox(
      "Status", 
      options=["All", "Active", "Inactive", "Expired", "Paused", "Up", "Down"],
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
    

#df = pd.DataFrame(data)
df = get_postings_with_platforms(coord_id)

if df.empty:
    st.info("No postings found. Please add a posting.")
else:
  # Status filter
  if status != "All":
      df = df[df["status"] == status]

  # Platform filter
  if platforms and "platform" in df.columns:
      df = df[df["platform"].isin(platforms)]

  # Sorting
  SORT_MAP = {
      "Title": "title",
      "Status": "status",
      "Applicants": "totalApplicants"
  }

  sort_column = SORT_MAP.get(sort)

  if sort_column and sort_column in df.columns:
      df = df.sort_values(by=sort_column)

  for col in ["postingID", "title", "status", "roleType", "platform", "totalApplicants"]:
    if col not in df.columns:
        df[col] = ""

  st.subheader("Job Postings Table", divider="gray")

  desired_order = ["postingID", "title", "status", "roleType", "platform", "totalApplicants"]

  df = df[desired_order]

  st.dataframe(df, use_container_width=True)

# =========================
# Delete a Job Posting
# =========================
st.subheader("Delete a Job Posting", divider="gray")
posting_id = st.text_input("Enter Posting ID to delete:")

if st.button("Delete Posting"):
    if posting_id:
        try:
            delete_url = f"http://web-api:4000/app_tracker/postings/{posting_id}"
            response = requests.delete(delete_url)
            if response.status_code == 200:
                st.success(f"Posting {posting_id} deleted successfully.")
                st.rerun()
            elif response.status_code == 404:
                st.warning(f"Posting {posting_id} not found.")
            else:
                st.error(f"Failed to delete posting: {response.text}")
        except Exception as e:
            st.error(f"Error deleting posting: {e}")
    else:
        st.warning("Please enter a valid Posting ID.")