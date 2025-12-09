# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/40_About.py", label="About", icon="🧠")



#### ------------------------ Career Coach Role ------------------------
def CareerCoachPageNav():
    st.sidebar.page_link("pages/50_Career_Coach_Home.py", label="Career Coach Home", icon="🏠")
    st.sidebar.page_link("pages/50_Career_Coach_Page.py", label="Career Coach Dashboard", icon="📊")
    st.sidebar.page_link("pages/50_Notifications_Page.py", label="Notifications", icon="🔔")
    st.sidebar.page_link("pages/50_Messages_Page.py", label="Messages", icon="✉️")


#### ------------------------ System Admin Role ------------------------
def AdminPageNav():
    st.sidebar.page_link("pages/20_Admin_Home_2.py", label="System Admin", icon="🖥️")


# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/Appli-Tracker.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:
            
        # If the user is a career coach, give them access to the career coach pages
        if st.session_state["role"] == "career_coach":
            CareerCoachPageNav()

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "administrator":
            AdminPageNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
