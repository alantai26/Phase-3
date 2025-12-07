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

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()
  
st.title('Career Coach Notifications')

def fetch_notifications(coach_id):
    try:
        r = requests.get(f"http://web-api:4000/app_tracker/career_coach/{coach_id}/notifications")
        if r.status_code == 200:
            return r.json()
        else:
            st.warning("No notifications found or error fetching notifications.")
            return []
    except Exception as e:
        st.error(f"Error fetching notifications: {e}")
        return []
    

def toggle_notifications(notification_ids, mark_read=True):
    try:
        r = requests.put(
            f"http://web-api:4000/app_tracker/career_coach/{coach_id}/notifications/toggle",
            json={"notification_ids": notification_ids, "mark_read": mark_read}
        )
        if r.status_code == 200:
            st.success(r.json().get("message"))
        else:
            st.error(r.json().get("error"))
    except Exception as e:
        st.error(f"Error updating notifications: {e}")

notifications = fetch_notifications(coach_id)

if notifications:
    with st.form("notifications_form"):
        checked_ids = []

        # Track which notifications are checked
        for n in notifications:
            dot = "🟢" if n.get("isRead") else "🔴"
            student_info = f" (Student ID: {n['studentID']})" if n.get("studentID") else ""
            checked = st.checkbox(
                f"{dot} {n['type']}{student_info}",
                value=n.get("isRead", False),
                key=f"notif_{n['notificationID']}"
            )
            if checked:
                checked_ids.append(n['notificationID'])

        col1, col2 = st.columns(2)
        with col1:
            mark_selected = st.form_submit_button("Mark Selected As Read")
            if mark_selected and checked_ids:
                toggle_notifications(checked_ids, mark_read=True)

        with col2:
            mark_unread = st.form_submit_button("Mark Selected As Unread")
            if mark_unread and checked_ids:
                toggle_notifications(checked_ids, mark_read=False)
