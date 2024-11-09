import streamlit as st

class MainApp:
    def __init__(self):
        self.session_state = st.session_state

    def initialize_session_state(self):
        if 'project' not in self.session_state:
            self.session_state['project'] = None
        if 'dark_mode' not in self.session_state:
            self.session_state['dark_mode'] = True
