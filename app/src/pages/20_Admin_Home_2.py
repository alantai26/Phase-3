import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

st.title('System Admin Dashboard')

# Status indicator
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**Status:** :green[Running]")
with col2:
    time_range = st.selectbox('Show:', ['Last 24 Hours', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days'])

time_map = {
    'Last 24 Hours': 1,
    'Last 7 Days': 7,
    'Last 30 Days': 30,
    'Last 90 Days': 90
}
days = time_map[time_range]

# Create tabs
tab1, tab2 = st.tabs(["System Management", "Data Security Management"])

with tab1:
    # Create left sidebar and main content area
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.markdown("### Performance Trackers")
        
        # Initialize session state for selected metric
        if 'selected_metric' not in st.session_state:
            st.session_state.selected_metric = 'response time'
        
        if st.button("DB Response Time Tracker", use_container_width=True, type="primary" if st.session_state.selected_metric == 'response time' else "secondary"):
            st.session_state.selected_metric = 'response time'
            st.rerun()
        
        if st.button("Resource Utilization Manager", use_container_width=True, type="primary" if st.session_state.selected_metric == 'cpu' else "secondary"):
            st.session_state.selected_metric = 'cpu'
            st.rerun()
        
        if st.button("Request Latency Tracker", use_container_width=True, type="primary" if st.session_state.selected_metric == 'latency' else "secondary"):
            st.session_state.selected_metric = 'latency'
            st.rerun()
        
        if st.button("DB Query Frequency", use_container_width=True, type="primary" if st.session_state.selected_metric == 'query frequency' else "secondary"):
            st.session_state.selected_metric = 'query frequency'
            st.rerun()
    
    with col_right:
        metric_type = st.session_state.selected_metric
        
        metric_names = {
            'response time': 'DB Query Response Time',
            'cpu': 'CPU Utilization',
            'latency': 'Request Latency',
            'query frequency': 'DB Query Frequency'
        }
        
        st.subheader(f"{metric_names.get(metric_type, 'Performance Metrics')}")
        
        try:
            response = requests.get(f'http://web-api:4000/app_tracker/sysadmin/stats/{metric_type}/{days}')
            response.raise_for_status()
            
            data = response.json()
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label=f"Average ({data.get('unit', 'N/A')})",
                    value=f"{data.get('avg_val', 0):.2f}"
                )
            
            with col2:
                st.metric(
                    label=f"Maximum ({data.get('unit', 'N/A')})",
                    value=f"{data.get('max_val', 0):.2f}"
                )
            
            with col3:
                st.metric(
                    label=f"Minimum ({data.get('unit', 'N/A')})",
                    value=f"{data.get('min_val', 0):.2f}"
                )
            
            with col4:
                st.metric(
                    label="Measurements",
                    value=f"{data.get('measurement_count', 0)}"
                )
            
            st.info(f"📊 Showing data from the {time_range.lower()}")
        except Exception as e:
            st.error(f"Unexpected error: No data available for the selected time period")

with tab2:
    st.subheader("Data Security Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Backup Status & Operations")
        st.info("Last Backup: Dec 5, 2025")
        st.info("Backup Health: Healthy")
        if st.button("Run Manual Backup", use_container_width=True):
            st.success("Backup initiated!")
        if st.button("Restore from Backup", use_container_width=True):
            st.success("Backup restored!")
    
    with col2:
        st.markdown("### Audit Log (Recent Activity)")
        st.write("Audit stuff")