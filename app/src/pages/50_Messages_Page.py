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
  
st.title('Career Coach Messages')

# Create tabs
tab1, = st.tabs(["Career Coach Messages"])

with tab1:
  st.write("This is where messages functionality will be implemented.")