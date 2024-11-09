import sqlite3
from typing import List, Dict, Optional
import json
import streamlit as st
from datetime import datetime

def init_db():
    """Initialize SQLite database for project management."""
    conn = sqlite3.connect('sparc_projects.db')
    c = conn.cursor()
    
    # Create projects table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  path TEXT NOT NULL,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  guidance TEXT,
                  status TEXT DEFAULT 'active')''')
                  
    # Create architectures table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS architectures
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER,
                  directory TEXT NOT NULL,
                  description TEXT,
                  model TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  files TEXT,
                  FOREIGN KEY(project_id) REFERENCES projects(id))''')
    
    conn.commit()
    conn.close()

def save_project(name: str, path: str, description: str, guidance: dict) -> bool:
    """Save project details to database."""
    try:
        conn = sqlite3.connect('sparc_projects.db')
        c = conn.cursor()
        c.execute('''INSERT INTO projects (name, path, description, guidance)
                     VALUES (?, ?, ?, ?)''', 
                  (name, path, description, json.dumps(guidance)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to save project: {str(e)}")
        return False

def get_projects() -> List[Dict]:
    """Get list of all projects."""
    try:
        conn = sqlite3.connect('sparc_projects.db')
        c = conn.cursor()
        c.execute('''SELECT id, name, path, description, created_at, updated_at, status 
                     FROM projects WHERE status = 'active' 
                     ORDER BY updated_at DESC''')
        projects = [{"id": row[0], "name": row[1], "path": row[2], 
                    "description": row[3], "created_at": row[4],
                    "updated_at": row[5], "status": row[6]}
                   for row in c.fetchall()]
        conn.close()
        return projects
    except Exception as e:
        st.error(f"Failed to get projects: {str(e)}")
        return []

def save_architecture(project_id: Optional[int], directory: str, description: str, 
                     model: str, files: Dict[str, str]) -> bool:
    """Save architecture details to database."""
    try:
        conn = sqlite3.connect('sparc_projects.db')
        c = conn.cursor()
        
        # Convert files dict to JSON string for storage
        files_json = json.dumps(files)
        
        c.execute('''INSERT INTO architectures 
                     (project_id, directory, description, model, files)
                     VALUES (?, ?, ?, ?, ?)''',
                  (project_id, directory, description, model, files_json))
        
        arch_id = c.lastrowid
        conn.commit()
        conn.close()
        return arch_id
    except Exception as e:
        st.error(f"Failed to save architecture: {str(e)}")
        return None

def get_architectures(project_id: Optional[int] = None) -> List[Dict]:
    """Get list of architectures, optionally filtered by project."""
    try:
        conn = sqlite3.connect('sparc_projects.db')
        c = conn.cursor()
        
        if project_id:
            c.execute('''SELECT id, directory, description, model, created_at, files 
                        FROM architectures WHERE project_id = ?
                        ORDER BY created_at DESC''', (project_id,))
        else:
            c.execute('''SELECT id, directory, description, model, created_at, files 
                        FROM architectures ORDER BY created_at DESC''')
            
        architectures = []
        for row in c.fetchall():
            arch = {
                "id": row[0],
                "directory": row[1],
                "description": row[2],
                "model": row[3],
                "created_at": row[4],
                "files": json.loads(row[5]) if row[5] else {}
            }
            architectures.append(arch)
            
        conn.close()
        return architectures
    except Exception as e:
        st.error(f"Failed to get architectures: {str(e)}")
        return []

def get_project_details(project_id: int) -> Optional[Dict]:
    """Get detailed project information."""
    try:
        conn = sqlite3.connect('sparc_projects.db')
        c = conn.cursor()
        c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "path": row[2],
                "description": row[3],
                "created_at": row[4],
                "updated_at": row[5],
                "guidance": json.loads(row[6]) if row[6] else {},
                "status": row[7]
            }
        return None
    except Exception as e:
        st.error(f"Failed to get project details: {str(e)}")
        return None
