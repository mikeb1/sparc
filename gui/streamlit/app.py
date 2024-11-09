import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="SPARC GUI",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode CSS
dark_mode_css = """
<style>
    /* Dark mode styles */
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stSidebar {
        background-color: #252526;
    }
    .stButton>button {
        background-color: #2D2D2D;
        color: #FFFFFF;
        border: 1px solid #3E3E3E;
    }
    .stTextInput>div>div>input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .stSelectbox>div>div>select {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
</style>
"""

# Inject dark mode CSS
st.markdown(dark_mode_css, unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.title("SPARC GUI")
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["Project", "Code", "Tests", "Settings"]
        )

    # Main content
    if page == "Project":
        st.title("Project Overview")
        st.write("Welcome to SPARC GUI!")
        
        # Project initialization
        with st.expander("Initialize New Project"):
            project_path = st.text_input("Project Path")
            if st.button("Create Project"):
                st.info("Project initialization coming soon...")

    elif page == "Code":
        st.title("Code Editor")
        st.info("Code editing features coming soon...")

    elif page == "Tests":
        st.title("Test Runner")
        st.info("Test execution features coming soon...")

    elif page == "Settings":
        st.title("Settings")
        with st.form("settings_form"):
            st.checkbox("Dark Mode (Always On)", value=True, disabled=True)
            st.text_input("Git Path")
            st.text_input("API Key", type="password")
            st.form_submit_button("Save Settings")

if __name__ == "__main__":
    main()
