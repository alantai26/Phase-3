import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

coach_id = st.session_state.get('coach_id')
SideBarLinks()

st.title("Career Coach Messages")


students = []
try:
    resp = requests.get(f"http://web-api:4000/app_tracker/career_coach/{coach_id}/students")
    if resp.status_code == 200:
        students = resp.json()
    else:
        st.error(f"Failed to fetch students: {resp.text}")
except Exception as e:
    st.error(f"Error fetching students: {str(e)}")

# Map studentID -> Name for display
student_map = {s["Student_ID"]: f'{s["First_Name"]} {s["Last_Name"]}' for s in students}

# Initialize session variables
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "selected_student" not in st.session_state:
    st.session_state.selected_student = None

left, right = st.columns([1, 2])

with left:
    st.subheader("Student List")
    st.write("---")
    for student_id, name in student_map.items():
        if st.button(name, use_container_width=True):
            st.session_state.selected_student = student_id
            # Fetch messages immediately when selecting a student
            try:
                msg_resp = requests.get(
                    f"http://web-api:4000/app_tracker/career_coach/{coach_id}/messages/{student_id}"
                )
                if msg_resp.status_code == 200:
                    raw_msgs = msg_resp.json()

                    normalized_msgs = []
                    for m in raw_msgs:
                        normalized_msgs.append({
                            "sender": m.get("sender", "Unknown"),
                            "content": m.get("content"),
                            "time": m.get("time") or m.get("dateTimeSent") or "unknown"
                        })
                    st.session_state.messages[student_id] = normalized_msgs
                else:
                    st.error(f"Failed to fetch messages: {msg_resp.text}")
                    st.session_state.messages[student_id] = []
            except Exception as e:
                st.error(f"Error fetching messages: {str(e)}")
                st.session_state.messages[student_id] = []


with right:
    st.subheader("Conversations")
    st.write("---")

    sid = st.session_state.selected_student
    if sid is None:
        st.info("Select a student to view messages.")
    else:
        # Display message history
        msgs = st.session_state.messages.get(sid, [])
        if not msgs:
            st.info("No messages yet.")
        else:
            for m in msgs:
                message_text = m.get("content")
                if message_text is None:
                    message_text = "[No content]"
                st.write(f"**{m.get('sender','Unknown')}:** {message_text}")

        st.write("---")

        # Right: Conversation
        user_msg_key = f"msg_input_{sid}"
        user_msg = st.text_input(
            "Type a message...", 
            key=user_msg_key, 
            value=""
        )

        if st.button("Send", key=f"send_btn_{sid}"):
            if user_msg.strip():
                try:
                    resp = requests.post(
                        f"http://web-api:4000/app_tracker/career_coach/{coach_id}/send_message",
                        json={"studentID": sid, "content": user_msg.strip()}
                    )
                    if resp.status_code == 200:
                        if sid not in st.session_state.messages:
                            st.session_state.messages[sid] = []
                        st.session_state.messages[sid].append({
                            "sender": "Coach",
                            "content": user_msg.strip(),
                            "time": "now"
                        })
                    else:
                        st.error(f"Failed to send message: {resp.text}")
                except Exception as e:
                    st.error(f"Error sending message: {str(e)}")