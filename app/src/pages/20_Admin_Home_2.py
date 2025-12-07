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

try:
    response = requests.get('http://web-api:4000/app_tracker/sysadmin/alerts/unresolved')
    if response.status_code == 200:
        alerts = response.json()
        if alerts:
            col_alert, col_btn = st.columns([3, 1])
            
            with col_alert:
                st.error(f" ALERT!! {len(alerts)} system issue(s) detected")
            
            with col_btn:
                if st.button("View Alerts →", type="primary", use_container_width=True):
                    st.switch_page("pages/31_Alerts_Management.py")
except Exception as e:
    st.error(f"Debug error: {str(e)}")

st.divider()

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
        
        if st.button("CPU Utilization Manager", use_container_width=True, type="primary" if st.session_state.selected_metric == 'cpu' else "secondary"):
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
            if response.status_code == 200:
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
                
                st.info(f" Showing data from the {time_range.lower()}")
            else:
                st.error(f"Error fetching data: {response.status_code}")
        except Exception as e:
            st.error(f"Unexpected error: No data available for the selected time period")

    st.divider()

    st.subheader(" Resource Usage Trends")
    
    try:
        response = requests.get(f'http://web-api:4000/app_tracker/sysadmin/resource-usage/{days}')
        if response.status_code == 200:
            usage_data = response.json()
            
            if usage_data:
                # Calculate overall averages
                total_users = sum(float(day.get('avg_active_users', 0)) for day in usage_data)
                total_apps = sum(float(day.get('avg_applications', 0)) for day in usage_data)
                total_cpu = sum(float(day.get('avg_cpu_usage', 0)) for day in usage_data)
                count = len(usage_data)
                
                # Display summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Avg Active Users", f"{total_users/count:.0f}")
                
                with col2:
                    st.metric("Avg Applications", f"{total_apps/count:.0f}")
                
                with col3:
                    st.metric("Avg CPU Usage", f"{total_cpu/count:.1f}%")
                
                st.divider()
                
                st.markdown("#### Daily Breakdown")
                
                # Create header
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.markdown("**Date**")
                with col2:
                    st.markdown("**Avg Users**")
                with col3:
                    st.markdown("**Max Users**")
                with col4:
                    st.markdown("**Avg Apps**")
                with col5:
                    st.markdown("**Avg CPU %**")
                
                st.divider()
                
                # Display each row
                for day in usage_data:
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    with col1:
                        st.write(day.get('usg_date', 'N/A'))
                    with col2:
                        st.write(f"{float(day.get('avg_active_users', 0)):.0f}")
                    with col3:
                        st.write(f"{float(day.get('max_active_users', 0)):.0f}")
                    with col4:
                        st.write(f"{float(day.get('avg_applications', 0)):.0f}")
                    with col5:
                        st.write(f"{float(day.get('avg_cpu_usage', 0)):.1f}")
            else:
                st.info("No resource usage data available")
        
    except Exception as e:
        st.error(f"Error fetching resource usage: {str(e)}")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Backup Status & Operations")
        
        # Fetch latest backup
        try:
            response = requests.get('http://web-api:4000/app_tracker/sysadmin/backups/latest')
            if response.status_code == 200:
                backup = response.json()
                
                st.write(f"**Last Backup:** {backup.get('datePerformed', 'N/A')}")
                st.write(f"**Backup Health:** {backup.get('health', 'Unknown')}")
                st.write(f"**Backup Size:** {backup.get('size', 'N/A')} GB" if backup.get('size') else "**Backup Size:** Calculating...")
                
                # Get retention policy from config
                try:
                    config_response = requests.get('http://web-api:4000/app_tracker/sysadmin/config/current')
                    if config_response.status_code == 200:
                        config = config_response.json()
                        st.write(f"**Retention Policy:** {config.get('daysToBackup', 'N/A')} days")
                    else:
                        st.write(f"**Retention Policy:** Not configured")
                except:
                    st.write(f"**Retention Policy:** Not configured")
            else:
                st.write("**Last Backup:** No backup history")
                st.write("**Backup Health:** Unknown")
                st.write("**Backup Size:** N/A")
                st.write("**Retention Policy:** N/A")
        except Exception as e:
            st.write("**Last Backup:** Error loading")
            st.write("**Backup Health:** Unknown")
            st.write("**Backup Size:** N/A")
            st.write("**Retention Policy:** N/A")
        
        st.write("") 
        
        if st.button("Run Manual Backup", use_container_width=True, type="primary"):
            try:
                response = requests.post('http://web-api:4000/app_tracker/sysadmin/backup/1')
                
                if response.status_code == 201:
                    result = response.json()
                    st.session_state.success_message = f" Backup initiated! ID: {result['backupID']}"
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Backup failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### Audit Log (Recent Activity)")
        
        try:
            hours = 99999 
            response = requests.get(f'http://web-api:4000/app_tracker/sysadmin/audit-logs/{hours}')
            
            if response.status_code == 200:
                logs = response.json()
                
                if logs:
                    # Create table header
                    col_t, col_u, col_a = st.columns([2, 2, 2])
                    with col_t:
                        st.markdown("**Time**")
                    with col_u:
                        st.markdown("**User**")
                    with col_a:
                        st.markdown("**Action**")
                    
                    for log in logs[:6]:
                        col_t, col_u, col_a = st.columns([2, 2, 2])
                        
                        with col_t:
                            timestamp = log.get('timeStamp', 'N/A')
                            if timestamp != 'N/A':
                                time_str = str(timestamp)
                                st.write(time_str)
                            else:
                                st.write('N/A')
                        
                        with col_u:
                            if log.get('studentID'):
                                st.write(f"Student #{log['studentID']}")
                            elif log.get('coachID'):
                                st.write(f"Coach #{log['coachID']}")
                            elif log.get('coordinatorID'):
                                st.write(f"Coordinator #{log['coordinatorID']}")
                            elif log.get('adminID'):
                                st.write(f"Admin #{log['adminID']}")
                            else:
                                st.write("Unknown")
                        
                        with col_a:
                            st.write(log.get('action', 'N/A'))
                else:
                    st.info("No recent audit activity")
            else:
                st.error(f"Error loading audit log")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    
    st.markdown("### Application Updates & Maintenance")
    
    col_left = st.columns(1)[0]
    
    with col_left:
        st.markdown("**Patch Notes**")
        
        # Patch notes text area
        patch_notes = st.text_area(
            "",
            value="- Security patch for SQL injection fix\n- Performance improvements\n- Bug fixes for notification system",
            height=150,
            label_visibility="collapsed"
        )
        
        st.write("")  
        
        # Update buttons
        col_btn1 = st.columns(1)[0]

        with col_btn1:
            if st.button("Schedule Update", use_container_width=True):
                st.switch_page("pages/21_System_Config.py")
                st.info("Update scheduled for maintenance window")