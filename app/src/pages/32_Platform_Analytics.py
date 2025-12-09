import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

coord_id = st.session_state.get('coordinator_id')

st.title('Platform Performance Analytics')
st.subheader("Student Activity", divider="gray")

col_postings, col_timeframe = st.columns(2)
with col_postings:
    posting_filter = st.selectbox(
        "Postings", 
        options=["All", "LinkedIn", "Indeed", "Handshake", "Company Website", "NUworks"],
        index=0
    )
with col_timeframe:
    timeframe_filter = st.selectbox(
        "Timeframe", 
        options=["Last 30 days", "Last 60 days", "All time"],
        index=2
    )

col_bar, col_pie = st.columns(2)

# Fetch applications from Flask API
def get_student_applications(coordinator_id):
    url = f"http://web-api:4000/app_tracker/coordinator/{coordinator_id}/applications"
    try:
        r = requests.get(url)

        if r.status_code != 200:
            st.error("Failed to load application data.")
            return pd.DataFrame()

        df = pd.DataFrame(r.json())
        return df
    except Exception as e:
        st.error(f"Request failed: {e}")
        return pd.DataFrame()

applications_df = get_student_applications(coord_id)

# Ensure applicationID exists
if 'applicationID' not in applications_df.columns:
    col_bar.write("No application data available.")
    col_pie.write("No application data available.")
else:
    applications_df = applications_df[applications_df['applicationID'].notna()]

    if not applications_df.empty:
        # Apply timeframe filter
        applications_df['dateApplied'] = pd.to_datetime(
            applications_df['dateApplied'],
            format="%a, %d %b %Y %H:%M:%S GMT",
            errors='coerce'
        )

        applications_df['dateApplied'] = applications_df['dateApplied'].dt.date

        if timeframe_filter == "Last 30 days":
            start_date = (pd.Timestamp.today() - pd.Timedelta(days=30)).date()
            applications_df = applications_df[applications_df['dateApplied'] >= start_date]
        elif timeframe_filter == "Last 60 days":
            start_date = (pd.Timestamp.today() - pd.Timedelta(days=60)).date()
            applications_df = applications_df[applications_df['dateApplied'] >= start_date]


        # Apply platform filter
        if posting_filter != "All":
            applications_df = applications_df[applications_df['platform'] == posting_filter]

        if applications_df.empty:
            col_bar.write("No application data for selected filters.")
            col_pie.write("No application data for selected filters.")
        else:
            # Bar Chart: Applicants by Platform
            platform_counts = applications_df.groupby('platform').size().sort_values(ascending=False)
            if platform_counts.empty:
                col_bar.write("No application data for bar chart.")
            else:
                fig2, ax2 = plt.subplots()
                ax2.bar(platform_counts.index, platform_counts.values, color='skyblue')
                ax2.set_title("Applicants by Platform")
                ax2.set_ylabel("Number of Applicants")
                ax2.set_xlabel("Platform")
                ax2.set_xticklabels(platform_counts.index, rotation=45, ha='right')
                max_val = platform_counts.max()
                ax2.set_ylim(0, max_val + 1 if max_val > 0 else 3)
                ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
                col_bar.pyplot(fig2, use_container_width=True)

            # Pie Chart: Successful Hires by Platform
            applications_df['stage_category'] = applications_df['stage'].str.lower().map({
                "applied": "Applied",
                "interviewing": "Interviewing",
                "offered": "Offered",
                "offer": "Offered"
            })

            successful_df = applications_df[applications_df['stage_category'] == "Offered"]
            if successful_df.empty:
                col_pie.write("No successful hires for selected filters.")
            else:
                platform_success_counts = successful_df.groupby('platform').size()
                fig1, ax1 = plt.subplots()
                ax1.pie(platform_success_counts, labels=platform_success_counts.index, autopct='%1.1f%%', startangle=90)
                ax1.set_title("Successful Hires by Platform")
                col_pie.pyplot(fig1, use_container_width=True)
    else:
        col_bar.write("No application data available.")
        col_pie.write("No application data available.")
