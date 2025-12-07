import logging
logger = logging.getLogger(__name__)


import streamlit as st
from modules.nav import SideBarLinks


st.set_page_config(layout = 'wide')


# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()


st.title(f"Welcome Career Coach, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')


if st.button('Checkout Career Coach Dashboard',
            type='primary',
            use_container_width=True):
        st.switch_page('pages/50_Career_Coach_Page.py')

if st.button('Checkout Messages',
            type='primary',
            use_container_width=True):
      st.switch_page('pages/50_Messages_Page.py')

if st.button('Checkout notifications',
          type='primary',
          use_container_width=True):
    st.switch_page('pages/50_Notifications_Page.py')

