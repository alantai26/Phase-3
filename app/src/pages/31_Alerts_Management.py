import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

st.title('Alert Management')

# Back button
if st.button("← Back to Dashboard"):
    st.switch_page("pages/20_Admin_Home_2.py")

st.divider()

try:
    response = requests.get('http://web-api:4000/app_tracker/sysadmin/alerts/unresolved')
    
    if response.status_code == 200:
        alerts = response.json()
        
        if alerts:
            st.subheader(f"Unresolved Alerts ({len(alerts)})")
            
            
            # Display Critical Alerts
            if alerts:
                for alert in alerts:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.error(f"**{alert['type']}** - {alert.get('message', 'No message')}")
                            st.caption(f"Time: {alert['timeStamp']} ({alert.get('mins_ago', 0)} minutes ago)")
                        
                        with col2:
                            if st.button(f"Resolve", key=f"resolve_critical_{alert['alertID']}", 
                                       type="primary", use_container_width=True):
                                try:
                                    resolve_response = requests.put(
                                        f"http://web-api:4000/app_tracker/sysadmin/alerts/{alert['alertID']}/resolve"
                                    )
                                    if resolve_response.status_code == 200:
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to resolve: {resolve_response.status_code}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        st.divider()
        else:
            st.success(" No unresolved alerts - All systems operating normally!")
    else:
        st.error(f"Error fetching alerts: {response.status_code}")
        
except Exception as e:
    st.error(f"Error fetching alerts: {str(e)}")

st.divider()

# Alert Statistics
st.subheader("Alert Statistics")

col1, col2, col3 = st.columns(3)

try:
    if response.status_code == 200 and alerts:
        with col1:
            st.metric("Total Unresolved", len(alerts))
        
        with col2:
            critical_count = len([a for a in alerts if a.get('severity') == 'Critical'])
            st.metric("Critical", critical_count, delta="Urgent" if critical_count > 0 else None)
        
        with col3:
            warning_count = len([a for a in alerts if a.get('severity') == 'Warning'])
            st.metric("Warnings", warning_count)
    else:
        st.success(" No unresolved alerts - All systems operating normally!")
except:
    pass