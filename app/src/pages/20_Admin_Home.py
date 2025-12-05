# This is the previous admin home page, now replaced by 20_Admin_Home_2.py

import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

st.title('System Admin Home Page')
st.header('System Performance (Last 24 Hours)')

col1, col2 = st.columns(2)

# Fetch speed stats
try:
    response = requests.get('http://web-api:4000/app_tracker/sysadmin/stats?type=speed')
    response.raise_for_status() 
    
    speed_data = response.json()
    with col1:
        st.metric(
            label=f"Speed ({speed_data.get('unit', 'N/A')})",
            value=f"{speed_data.get('avg_val', 0):.2f}",
            delta=f"Max: {speed_data.get('max_val', 0):.2f}"
        )
except Exception as e:
    with col1:
        st.error(f"Unexpected error: {str(e)}")

# Fetch traffic stats
try:
    response = requests.get('http://web-api:4000/app_tracker/sysadmin/stats?type=traffic')
    response.raise_for_status()
    
    traffic_data = response.json()
    with col2:
        st.metric(
            label=f"Traffic ({traffic_data.get('unit', 'N/A')})",
            value=f"{traffic_data.get('avg_val', 0):.2f}",
            delta=f"Max: {traffic_data.get('max_val', 0):.2f}"
        )
except Exception as e:
    with col2:
        st.error(f"Unexpected error: {str(e)}")

st.divider()