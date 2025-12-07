import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

st.title('System Configuration')

# Back button
if st.button("← Back to Dashboard"):
    st.switch_page("pages/20_Admin_Home_2.py")

st.divider()

# Fetch current configuration
try:
    response = requests.get('http://web-api:4000/app_tracker/sysadmin/config/current')
    
    if response.status_code == 200:
        current_config = response.json()
        
        st.info(f"**Current Configuration** | Last Modified: {current_config.get('lastModifiedDate', '2025-01-01 00:00:00')} by {current_config.get('modified_by', 'Unknown')}")
        
        # Display current settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Backup Settings")
            st.write(f"**Schedule:** {current_config.get('backupSchedule', 'Not set')}")
            st.write(f"**Retention:** {current_config.get('daysToBackup', 'N/A')} days")
        
        with col2:
            st.markdown("#### Alert Thresholds")
            st.write(f"**CPU Threshold:** {'Enabled' if current_config.get('alertThresholdCPU') else 'Disabled'}")
            st.write(f"**Query Time Threshold:** {'Enabled' if current_config.get('alertThresholdQueryTime') else 'Disabled'}")
        
        st.divider()
    else:
        st.warning("No configuration found - create a new one below")
        current_config = {}
        
except Exception as e:
    st.error(f"Error fetching configuration: {str(e)}")
    current_config = {}

# Create new configuration form
st.subheader("Update System Configuration")

with st.form("config_form"):
    st.markdown("#### Backup Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        backup_schedule = st.text_input(
            "Backup Schedule",
            value=current_config.get('backupSchedule', '2025-12-10 02:00:00'),
            help="Format: YYYY-MM-DD HH:MM:SS"
        )
        
        days_to_backup = st.number_input(
            "Backup Retention (days)",
            min_value=1,
            value=current_config.get('daysToBackup', 1)
        )
    
    with col2:
        data_retention = st.number_input(
            "Data Retention Time (days)",
            min_value=1,
            value=current_config.get('dataRetentionTime', 1),
            help="How long to keep old data"
        )
    
    st.markdown("#### Alert Thresholds")
    col3, col4 = st.columns(2)
    
    with col3:
        cpu_threshold = st.checkbox(
            "Enable CPU Alert Threshold",
            value=current_config.get('alertThresholdCPU', False)
        )
    
    with col4:
        query_threshold = st.checkbox(
            "Enable Query Time Alert Threshold",
            value=current_config.get('alertThresholdQueryTime', False)
        )
    
    st.markdown("#### Maintenance Window")
    col5, col6 = st.columns(2)
    
    with col5:
        maintenance_start = st.text_input(
            "Maintenance Start",
            value=current_config.get('maintenanceStartDateTime', '2025-12-08 02:00:00'),
            help="Format: YYYY-MM-DD HH:MM:SS"
        )
    
    with col6:
        maintenance_end = st.text_input(
            "Maintenance End",
            value=current_config.get('maintenanceEndDateTIme', '2025-12-08 04:00:00'),
            help="Format: YYYY-MM-DD HH:MM:SS"
        )
    
    # Submit button
    submitted = st.form_submit_button("Save Configuration", type="primary", use_container_width=True)
    
    if submitted:
        try:
            config_data = {
                'backupSchedule': backup_schedule,
                'daysToBackup': days_to_backup,
                'alertThresholdCPU': 1 if cpu_threshold else 0,
                'alertThresholdQueryTime': 1 if query_threshold else 0,
                'dataRetentionTime': data_retention,
                'maintenanceStartDateTime': maintenance_start,
                'maintenanceEndDateTime': maintenance_end
            }
            
            response = requests.post(
                'http://web-api:4000/app_tracker/sysadmin/config/1',
                json=config_data
            )
            
            if response.status_code == 201:
                result = response.json()
                st.success(f" {result['message']}")
                st.info(f"Configuration ID: {result['configID']}")
            else:
                st.error(f"Failed to save configuration: {response.status_code}")
            
        except Exception as e:
            st.error(f"Failed to save configuration: {str(e)}")
