import streamlit as st
import subprocess

# Configure Streamlit page - must be first Streamlit command
st.set_page_config(
    page_title="SPARC GUI",
    page_icon="🔧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import remaining modules after st.set_page_config()
import streamlit.components.v1 as components
import sys
from pathlib import Path
import base64
import os
import git
import toml
from datetime import datetime

# Add parent directory to Python path to find utils module
sys.path.append(str(Path(__file__).parent.parent))

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
            ["Project", "Code", "Tests", "Settings"],
            key="nav_radio"
        )

    # Main content
    if page == "Project":
        from utils.database import init_db, save_project, get_projects
        from utils.project import scan_architecture_folders, load_project_files, init_git_repo
        from utils.ui import (show_project_setup_instructions, show_project_card, 
                            show_architecture_folder_card)
        
        init_db()  # Ensure database exists
        
        st.title("Project Management")
        
        # Top-level tabs
        tab1, tab2, tab3 = st.tabs(["📚 Getting Started", "🆕 New Project", "📂 Existing Projects"])
        
        with tab1:
            show_project_setup_instructions()
            
        with tab2:
            st.header("Create New Project")

            # Get recent projects and architecture folders for dropdowns
            recent_projects = get_projects()
            base_path = "."  # Configure base path for architecture folders
            arch_folders = scan_architecture_folders(base_path)
            
            # Project details form
            with st.form("new_project"):
                # Dropdowns for importing
                col1, col2 = st.columns(2)
                with col1:
                    selected_project = st.selectbox(
                        "Import from Recent Project",
                        ["None"] + [p['name'] for p in recent_projects],
                        key="import_recent"
                    )
                with col2:
                    selected_arch = st.selectbox(
                        "Import from Architecture",
                        ["None"] + [f['name'] for f in arch_folders],
                        key="import_arch"
                    )

                # Update name and path based on selection
                default_name = ""
                default_path = ""
                
                if selected_project != "None":
                    try:
                        project = next(p for p in recent_projects if p['name'] == selected_project)
                        default_name = f"{project['name']}_new"
                        default_path = str(Path(project['path']).parent / default_name)
                    except StopIteration:
                        st.error(f"Could not find project: {selected_project}")
                elif selected_arch != "None":
                    try:
                        arch = next(f for f in arch_folders if f['name'] == selected_arch)
                        # Extract timestamp and title from architecture folder name
                        parts = arch['name'].split('_', 2)  # Split into ['architecture', 'timestamp', 'title']
                        if len(parts) >= 3:
                            default_name = parts[2]  # Use the title part
                            default_path = str(Path(arch['path']).parent / default_name)
                        else:
                            default_name = arch['name'].replace('architecture_', '')
                            default_path = str(Path(arch['path']).parent / default_name)
                        
                        # Update form values immediately when architecture is selected
                        st.session_state['project_name'] = default_name
                        st.session_state['project_path'] = default_path
                    except StopIteration:
                        st.error(f"Could not find architecture: {selected_arch}")

                name = st.text_input("Project Name", 
                                   value=default_name,
                                   key="project_name")
                description = st.text_area("Project Description")
                path = st.text_input("Project Path", 
                                   value=default_path,
                                   key="project_path")
                
                col1, col2 = st.columns(2)
                with col1:
                    init_git = st.checkbox("Initialize Git Repository", value=True)
                with col2:
                    create_arch = st.checkbox("Generate Architecture", value=True)
                    
                if st.form_submit_button("Create Project"):
                    if name and path:
                        # Create project directory
                        try:
                            project_dir = Path(path)
                            project_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Initialize git if requested
                            if init_git:
                                repo = init_git_repo(path)
                            
                            # Save to database
                            if save_project(name, str(project_dir), description, {}):
                                st.success("Project created successfully!")
                                if create_arch:
                                    st.info("Generating architecture files...")
                                    # Add architecture generation logic here
                        except Exception as e:
                            st.error(f"Failed to create project: {str(e)}")
                    else:
                        st.error("Please provide project name and path")
            
        with tab3:
            col1, col2 = st.columns([2,1])
            
            st.subheader("Recent Projects")
            projects = get_projects()
            for project in projects:
                with st.container():
                    st.markdown(f"### 📁 {project['name']}")
                    st.text(f"Path: {project['path']}")
                    if project.get('description'):
                        description = st.text_area(
                            "Description", 
                            project['description'],
                            key=f"desc_{project['id']}"
                        )
                        if description != project['description']:
                            # Add logic to save updated description
                            pass
                            
                    st.text(f"Created: {project['created_at']}")
                    st.text(f"Status: {project['status']}")
                    
                    # Add MD file editing
                    arch_dir = Path(project['path']) / "architecture"
                    if arch_dir.exists():
                        st.markdown("#### Architecture Files:")
                        for md_file in arch_dir.glob("*.md"):
                            with st.expander(f"📄 {md_file.name}"):
                                content = md_file.read_text()
                                new_content = st.text_area(
                                    f"Edit {md_file.name}", 
                                    content,
                                    height=300,
                                    key=f"md_{project['id']}_{md_file.name}"
                                )
                                if new_content != content:
                                    try:
                                        md_file.write_text(new_content)
                                        st.success(f"Saved changes to {md_file.name}")
                                    except Exception as e:
                                        st.error(f"Failed to save {md_file.name}: {str(e)}")
                    
                    if st.button("Load Project", key=f"load_{project['id']}"):
                        st.session_state.project = project
                        st.experimental_rerun()
                    
                    st.markdown("---")
            
            st.subheader("Architecture Folders")
            base_path = "."  # Configure this path as needed
            arch_folders = scan_architecture_folders(base_path)
            for folder in arch_folders:
                with st.container():
                    st.markdown(f"### 🏗️ {folder['name']}")
                    st.text(f"Created: {folder['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if folder['guidance']:
                        st.text("Guidance file found")
                        if st.button("View Guidance", key=f"guidance_{folder['path']}"):
                            with st.expander("Guidance Details"):
                                st.json(folder['guidance'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Import as Project", key=f"import_{folder['path']}"):
                            # Handle import
                            pass
                    with col2:
                        if st.button("View Files", key=f"view_{folder['path']}"):
                            st.session_state.selected_folder = folder['path']
                    
                    st.markdown("---")

    elif page == "Code":
        st.title("🚀 SPARC Code Generator")
        
        tab1, tab2 = st.tabs(["📝 CLI Options", "⚙️ Guidance Configuration"])
        
        with tab1:
            st.header("Command Line Options")
            
            # Mode Selection
            mode = st.radio(
                "Select Mode",
                ["🏗️ Architect", "💻 Implement"],
                help="Choose between generating architecture or implementing code"
            )
            
            # Common Options
            model = st.selectbox(
                "🤖 AI Model",
                ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "gpt-4", "gpt-4-turbo"],
                help="Select the AI model to use"
            )
            
            if mode == "🏗️ Architect":
                # Architect mode options
                project_desc = st.text_area(
                    "📋 Project Description",
                    help="Describe your project in detail"
                )
                guidance_file = st.text_input(
                    "📁 Guidance File Path",
                    value="guidance.toml",
                    help="Path to your guidance TOML file"
                )
                
            else:
                # Implement mode options
                col1, col2 = st.columns(2)
                with col1:
                    max_attempts = st.number_input(
                        "🔄 Max Attempts",
                        min_value=1,
                        value=3,
                        help="Maximum implementation attempts per component"
                    )
                with col2:
                    guidance_file = st.text_input(
                        "📁 Guidance File Path",
                        value="guidance.toml",
                        help="Path to your guidance TOML file"
                    )
                
                optional_desc = st.text_area(
                    "📝 Optional Description",
                    help="Additional implementation details (optional)"
                )
            
            # Generate Button
            if st.button("🚀 Generate", type="primary"):
                if mode == "🏗️ Architect" and not project_desc:
                    st.error("Please provide a project description")
                else:
                    with st.spinner("Generating..."):
                        try:
                            # Construct command
                            cmd = ["python", "sparc_cli.py"]
                            cmd.extend([mode.split()[1].lower()])
                            cmd.extend(["--model", model])
                            cmd.extend(["--guidance-file", guidance_file])
                            
                            if mode == "🏗️ Architect":
                                cmd.append(project_desc)
                            else:
                                cmd.extend(["--max-attempts", str(max_attempts)])
                                if optional_desc:
                                    cmd.append(optional_desc)
                                    
                            # Execute command
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                st.success("Generation completed successfully!")
                                with st.expander("View Details"):
                                    st.code(result.stdout)
                            else:
                                st.error("Generation failed")
                                with st.expander("View Error"):
                                    st.code(result.stderr)
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
        
        with tab2:
            st.header("Guidance Configuration")
            
            # Project Settings
            st.subheader("🎯 Project Settings")
            col1, col2 = st.columns(2)
            with col1:
                framework = st.text_input("Framework", help="e.g., Flask, Next.js")
                language = st.selectbox(
                    "Language",
                    [
                        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
                        "Rust", "Swift", "Kotlin", "Ruby", "PHP", "Scala", "R",
                        "MATLAB", "Dart", "Lua", "Haskell", "Erlang", "Elixir",
                        "Clojure", "F#", "OCaml", "Julia", "Groovy", "Perl",
                        "Assembly", "COBOL", "Fortran", "Ada", "Prolog",
                        "Lisp", "Scheme", "Racket", "Smalltalk", "Pascal",
                        "VHDL", "Verilog", "D", "Nim", "Crystal", "Zig",
                        "Objective-C", "Visual Basic", "Delphi", "ActionScript",
                        "CoffeeScript", "Elm", "PureScript", "Reason", "Hack",
                        "ABAP", "RPG", "Apex", "PowerShell", "Bash", "TCL",
                        "Forth", "APL", "J", "Q", "K", "Wolfram", "SQL",
                        "PL/SQL", "T-SQL", "HiveQL", "SPARQL", "Cypher",
                        "WebAssembly", "Solidity", "Move", "Cairo"
                    ],
                    help="Select the primary programming language"
                )
            with col2:
                features = st.text_area("Features (one per line)", help="List key features")
            
            # Implementation Settings
            st.subheader("⚙️ Implementation Settings")
            col1, col2 = st.columns(2)
            with col1:
                max_attempts = st.number_input("Max Attempts", min_value=1, value=3)
                test_first = st.checkbox("Test First Approach", value=True)
            with col2:
                type_hints = st.checkbox("Type Hints", value=True)
                docstring_style = st.selectbox("Docstring Style", ["Google", "NumPy", "reStructuredText"])
            
            # Testing Requirements
            st.subheader("🧪 Testing Requirements")
            col1, col2 = st.columns(2)
            with col1:
                min_coverage = st.slider("Minimum Coverage %", 0, 100, 85)
                unit_test = st.checkbox("Unit Tests Required", value=True)
            with col2:
                integration_test = st.checkbox("Integration Tests Required", value=True)
            
            # Quality Settings
            st.subheader("✨ Code Quality")
            col1, col2 = st.columns(2)
            with col1:
                max_complexity = st.number_input("Max Complexity", min_value=1, value=8)
                max_line_length = st.number_input("Max Line Length", min_value=50, value=88)
            with col2:
                require_type_hints = st.checkbox("Require Type Hints", value=True)
                require_docstrings = st.checkbox("Require Docstrings", value=True)
            
            # Generate Files
            if st.button("📝 Generate Files", type="primary"):
                try:
                    # Generate guidance content
                    guidance_content = {
                        "project": {
                            "framework": framework,
                            "language": language,
                            "features": [f.strip() for f in features.split('\n') if f.strip()]
                        },
                        "implementation": {
                            "max_attempts": max_attempts,
                            "test_first": test_first,
                            "type_hints": type_hints,
                            "docstring_style": docstring_style
                        },
                        "testing": {
                            "min_coverage": min_coverage,
                            "unit_test_required": unit_test,
                            "integration_test_required": integration_test
                        },
                        "quality": {
                            "max_complexity": max_complexity,
                            "max_line_length": max_line_length,
                            "require_type_hints": require_type_hints,
                            "require_docstrings": require_docstrings
                        }
                    }
                    
                    # Convert to TOML string
                    toml_str = toml.dumps(guidance_content)

                    # Generate markdown files
                    files_content = {
                        "Specification.md": """# Specification
...
""",
                        "Architecture.md": """# Architecture
...
""",
                        "Pseudocode.md": """# Pseudocode
...
""",
                        "Refinement.md": """# Refinement
...
""",
                        "Completion.md": """# Completion
...
"""
                    }

                    # Display previews in tabs
                    tabs = st.tabs(["📋 TOML", "📑 Specification", "🏗️ Architecture", 
                                  "💻 Pseudocode", "🔄 Refinement", "✅ Completion"])
                    
                    with tabs[0]:
                        st.code(toml_str, language="toml")
                        st.download_button(
                            "💾 Download guidance.toml",
                            toml_str,
                            "guidance.toml",
                            "text/toml",
                            use_container_width=True
                        )

                    for i, (filename, content) in enumerate(files_content.items(), 1):
                        with tabs[i]:
                            st.markdown(content)
                            st.download_button(
                                f"💾 Download {filename}",
                                content,
                                filename,
                                "text/markdown",
                                use_container_width=True
                            )
                    
                except Exception as e:
                    st.error(f"Failed to generate files: {str(e)}")

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
