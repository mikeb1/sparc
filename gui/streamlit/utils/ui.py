import streamlit as st
from typing import Dict, List
from datetime import datetime

def show_project_setup_instructions():
    """Display step-by-step project setup instructions."""
    st.markdown("""
    ## Getting Started with SPARC
    
    Follow these steps to set up your project:
    
    ### 1. Choose Project Location
    - Select or create a directory for your project
    - Ensure you have write permissions
    - Consider version control requirements
    
    ### 2. Project Configuration
    - Provide a descriptive project name
    - Add a detailed project description
    - Configure initial settings
    
    ### 3. Architecture Setup
    - Review generated architecture files
    - Customize components as needed
    - Validate project structure
    
    ### 4. Version Control
    - Initialize git repository
    - Set up initial commit
    - Configure remote repository (optional)
    """)

def show_project_card(project: Dict):
    """Display a project card with key information."""
    with st.expander(f"📁 {project['name']}", expanded=False):
        col1, col2 = st.columns([2,1])
        
        with col1:
            st.text(f"Path: {project['path']}")
            if project.get('description'):
                st.text(f"Description: {project['description']}")
                
        with col2:
            st.text(f"Created: {project['created_at']}")
            st.text(f"Status: {project['status']}")
            
        if st.button("Load Project", key=f"load_{project['id']}"):
            return project['id']
    return None

def show_architecture_folder_card(folder: Dict):
    """Display an architecture folder card."""
    with st.expander(f"🏗️ {folder['name']}", expanded=False):
        st.text(f"Created: {folder['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if folder['guidance']:
            st.text("Guidance file found:")
            st.json(folder['guidance'])
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Import as Project", key=f"import_{folder['path']}"):
                return folder
        with col2:
            if st.button("View Files", key=f"view_{folder['path']}"):
                st.session_state.selected_folder = folder['path']
    return None
