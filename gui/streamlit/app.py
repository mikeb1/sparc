import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os
import git
import toml
from datetime import datetime

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

def init_session_state():
    """Initialize session state variables."""
    if 'project_path' not in st.session_state:
        st.session_state.project_path = None
    if 'components' not in st.session_state:
        st.session_state.components = []
    if 'git_repo' not in st.session_state:
        st.session_state.git_repo = None

def load_project(path: str) -> bool:
    """Load an existing SPARC project."""
    try:
        project_dir = Path(path)
        if not project_dir.exists():
            st.error(f"Project directory does not exist: {path}")
            return False
            
        # Check for architecture files
        arch_dir = project_dir / "architecture"
        if not arch_dir.exists() or not any(arch_dir.iterdir()):
            st.error("No architecture files found. Please initialize project first.")
            return False
            
        # Load guidance if exists
        guidance_file = project_dir / "guidance.toml"
        if guidance_file.exists():
            with open(guidance_file) as f:
                st.session_state.guidance = toml.load(f)
                
        # Setup git repo
        try:
            st.session_state.git_repo = git.Repo(path)
        except git.InvalidGitRepositoryError:
            st.warning("Git repository not initialized")
            
        st.session_state.project_path = path
        return True
        
    except Exception as e:
        st.error(f"Failed to load project: {str(e)}")
        return False

def show_project_status():
    """Display project status information."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Project Info")
        st.text(f"Location: {st.session_state.project_path}")
        
        # Show architecture files
        arch_dir = Path(st.session_state.project_path) / "architecture"
        if arch_dir.exists():
            files = list(arch_dir.glob("*.md"))
            st.write("Architecture Files:")
            for f in files:
                st.text(f"- {f.name}")
                
    with col2:
        st.subheader("Git Status")
        if st.session_state.git_repo:
            repo = st.session_state.git_repo
            st.text(f"Branch: {repo.active_branch.name}")
            st.text(f"Last Commit: {repo.head.commit.message}")
            
            # Show changes
            if repo.is_dirty():
                st.warning("Uncommitted Changes:")
                for item in repo.index.diff(None):
                    st.text(f"- Modified: {item.a_path}")
        else:
            st.warning("Git not initialized")

def show_components():
    """Display project components."""
    st.subheader("Components")
    
    # Read components from Architecture.md
    arch_file = Path(st.session_state.project_path) / "architecture" / "Architecture.md"
    if arch_file.exists():
        content = arch_file.read_text()
        
        # Extract components using simple parsing
        import re
        components = re.findall(r'## Component: (\w+)', content)
        
        if components:
            for comp in components:
                with st.expander(comp):
                    st.text("Status: Implemented")
                    if st.button(f"View {comp} Details", key=f"view_{comp}"):
                        st.session_state.selected_component = comp
        else:
            st.info("No components defined in Architecture.md")
    else:
        st.error("Architecture.md not found")

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
        init_session_state()
        
        st.title("Project Overview")
        
        if not st.session_state.project_path:
            # Project initialization section
            st.write("Initialize or Load Project")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("New Project")
                new_path = st.text_input("Project Path", placeholder="/path/to/project")
                if st.button("Create Project"):
                    if new_path:
                        try:
                            # Create project directory
                            project_dir = Path(new_path)
                            project_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Initialize git
                            git.Repo.init(project_dir)
                            
                            # Load the project
                            if load_project(new_path):
                                st.success("Project created successfully!")
                            
                        except Exception as e:
                            st.error(f"Failed to create project: {str(e)}")
                    else:
                        st.error("Please enter a project path")
            
            with col2:
                st.subheader("Load Existing")
                existing_path = st.text_input("Project Path", placeholder="/path/to/existing")
                if st.button("Load Project"):
                    if existing_path:
                        if load_project(existing_path):
                            st.success("Project loaded successfully!")
                    else:
                        st.error("Please enter a project path")
                        
        else:
            # Project status and management
            show_project_status()
            
            st.markdown("---")
            
            show_components()
            
            # Project actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Refresh Status"):
                    load_project(st.session_state.project_path)
                    
            with col2:
                if st.button("Clear Project"):
                    st.session_state.project_path = None
                    st.session_state.git_repo = None
                    st.experimental_rerun()
                    
            with col3:
                if st.session_state.git_repo and st.session_state.git_repo.is_dirty():
                    if st.button("Commit Changes"):
                        try:
                            repo = st.session_state.git_repo
                            repo.git.add(A=True)
                            repo.index.commit(f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            st.success("Changes committed successfully!")
                        except Exception as e:
                            st.error(f"Failed to commit changes: {str(e)}")

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
