import streamlit as st

class MainApp:
    def __init__(self):
        self.session_state = self.initialize_session_state()
        self.theme = self.setup_theme()
        self.sidebar = self.create_sidebar()

    def initialize_session_state(self):
        if 'project' not in st.session_state:
            st.session_state['project'] = None
        if 'dark_mode' not in st.session_state:
            st.session_state['dark_mode'] = True

    def setup_theme(self):
        st.set_page_config(layout="wide", initial_sidebar_state="expanded")
        if st.session_state.get('dark_mode', True):
            self.apply_dark_mode_css()  # You need to define this function to apply your CSS

    def apply_dark_mode_css(self):
        # Define your CSS application logic here
        pass

    def create_sidebar(self):
        with st.sidebar:
            st.image("path/to/logo.png")  # Replace with the correct path to your logo
            st.title("SPARC GUI")
            selected_page = st.radio("Navigation", ["Project", "Code", "Tests", "Settings"])
        return selected_page
    def run(self):
        selected_page = self.create_sidebar()
        if selected_page == "Project":
            self.show_project_page()
        elif selected_page == "Code":
            self.show_code_editor()
        elif selected_page == "Tests":
            self.show_test_runner()
        elif selected_page == "Settings":
            self.show_settings()

    def show_project_page(self):
        st.title("Project Overview")
        # Add project page logic here

    def show_code_editor(self):
        st.title("Code Editor")
        # Add code editor logic here

    def show_test_runner(self):
        st.title("Test Runner")
        # Add test runner logic here

    def show_settings(self):
        st.title("Settings")
        # Add settings logic here
