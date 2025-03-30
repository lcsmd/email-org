#!/usr/bin/env python3
"""
Email Organization Application Setup Script
This script sets up the Email Organization application by:
1. Creating the necessary directory structure
2. Parsing the email_org.txt file to extract individual modules and configurations
3. Setting up a virtual environment
4. Installing required packages
5. Placing files in appropriate directories
"""

import os
import re
import sys
import subprocess
import shutil
import hashlib
import json
from pathlib import Path

# Define the base directory
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
EMAIL_ORG_FILE = BASE_DIR / "email_org.txt"

# Define directory structure
DIRECTORIES = {
    "app": {
        "api": {},
        "auth": {},
        "database": {},
        "email_processing": {},
        "frontend": {
            "static": {
                "css": {},
                "js": {},
                "img": {}
            },
            "templates": {}
        },
        "models": {},
        "utils": {},
        "ai": {}
    },
    "data": {
        "attachments": {},
        "bodies": {},
        "html_objects": {},
        "emails": {},
        "threads": {},
        "disclaimers": {}
    },
    "config": {},
    "logs": {},
    "tests": {}
}

# Define file sections to extract from email_org.txt
FILE_SECTIONS = {
    "# REQUIREMENTS.TXT": {"path": "requirements.txt", "type": "text"},
    "# CONFIG.JSON": {"path": "config/config.json", "type": "json"},
    "# DATABASE_MODELS.PY": {"path": "app/models/database_models.py", "type": "python"},
    "# EMAIL_PROCESSOR.PY": {"path": "app/email_processing/email_processor.py", "type": "python"},
    "# EMAIL_RETRIEVER.PY": {"path": "app/email_processing/email_retriever.py", "type": "python"},
    "# EMAIL_PARSER.PY": {"path": "app/email_processing/email_parser.py", "type": "python"},
    "# ATTACHMENT_HANDLER.PY": {"path": "app/email_processing/attachment_handler.py", "type": "python"},
    "# HTML_PROCESSOR.PY": {"path": "app/email_processing/html_processor.py", "type": "python"},
    "# THREAD_MANAGER.PY": {"path": "app/email_processing/thread_manager.py", "type": "python"},
    "# DATABASE_MANAGER.PY": {"path": "app/database/database_manager.py", "type": "python"},
    "# SEARCH_ENGINE.PY": {"path": "app/utils/search_engine.py", "type": "python"},
    "# RULE_ENGINE.PY": {"path": "app/utils/rule_engine.py", "type": "python"},
    "# CATEGORY_MANAGER.PY": {"path": "app/utils/category_manager.py", "type": "python"},
    "# AUTH_MANAGER.PY": {"path": "app/auth/auth_manager.py", "type": "python"},
    "# API_ROUTES.PY": {"path": "app/api/api_routes.py", "type": "python"},
    "# APP.PY": {"path": "app/app.py", "type": "python"},
    "# AI_ASSISTANT.PY": {"path": "app/ai/ai_assistant.py", "type": "python"},
    "# UTILS.PY": {"path": "app/utils/utils.py", "type": "python"},
    "# INDEX.HTML": {"path": "app/frontend/templates/index.html", "type": "html"},
    "# STYLE.CSS": {"path": "app/frontend/static/css/style.css", "type": "css"},
    "# MAIN.JS": {"path": "app/frontend/static/js/main.js", "type": "javascript"},
    "# README.MD": {"path": "README.md", "type": "markdown"},
    "# INIT_DB.PY": {"path": "app/database/init_db.py", "type": "python"},
    "# INIT_APP.PY": {"path": "init_app.py", "type": "python"}
}

def create_directory_structure(base_dir, structure, current_path=None):
    """Create the directory structure recursively."""
    if current_path is None:
        current_path = base_dir
    
    for dir_name, sub_dirs in structure.items():
        new_dir = current_path / dir_name
        new_dir.mkdir(exist_ok=True)
        print(f"Created directory: {new_dir}")
        
        if sub_dirs:
            create_directory_structure(base_dir, sub_dirs, new_dir)

def extract_file_sections(email_org_file, file_sections):
    """Extract file sections from the email_org.txt file."""
    if not email_org_file.exists():
        print(f"Error: {email_org_file} not found.")
        sys.exit(1)
    
    with open(email_org_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all section markers and their content
    extracted_files = {}
    
    for marker, file_info in file_sections.items():
        pattern = f"{marker}(.*?)(?=# [A-Z_]+\\.(?:PY|TXT|JSON|HTML|CSS|JS|MD)|$)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section_content = match.group(1).strip()
            extracted_files[file_info["path"]] = {
                "content": section_content,
                "type": file_info["type"]
            }
        else:
            print(f"Warning: Section {marker} not found in {email_org_file}")
    
    return extracted_files

def write_extracted_files(base_dir, extracted_files):
    """Write the extracted file sections to their respective files."""
    for file_path, file_info in extracted_files.items():
        full_path = base_dir / file_path
        
        # Ensure the parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(file_info["content"])
        
        print(f"Created file: {full_path}")

def setup_virtual_environment(base_dir):
    """Set up a virtual environment and install required packages."""
    venv_dir = base_dir / "venv"
    
    # Create virtual environment
    print("Setting up virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Determine the pip path based on the OS
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / "Scripts" / "pip"
    else:  # Unix/Linux/Mac
        pip_path = venv_dir / "bin" / "pip"
    
    # Install requirements
    requirements_file = base_dir / "requirements.txt"
    if requirements_file.exists():
        print("Installing required packages...")
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
    else:
        print("Warning: requirements.txt not found.")

def main():
    """Main function to set up the Email Organization application."""
    print("Starting Email Organization Application Setup...")
    
    # Create directory structure
    print("\nCreating directory structure...")
    create_directory_structure(BASE_DIR, DIRECTORIES)
    
    # Extract file sections
    print("\nExtracting file sections from email_org.txt...")
    extracted_files = extract_file_sections(EMAIL_ORG_FILE, FILE_SECTIONS)
    
    # Write extracted files
    print("\nWriting extracted files...")
    write_extracted_files(BASE_DIR, extracted_files)
    
    # Setup virtual environment
    print("\nSetting up virtual environment...")
    setup_virtual_environment(BASE_DIR)
    
    print("\nSetup completed successfully!")
    print("\nTo start the application, activate the virtual environment and run:")
    if os.name == 'nt':  # Windows
        print("venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("source venv/bin/activate")
    print("python init_app.py")

if __name__ == "__main__":
    main()
