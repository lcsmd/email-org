import os
import sys
import re
import shutil
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Directory structure
DIRECTORIES = [
    "app",
    "app/api",
    "app/auth",
    "app/database",
    "app/email_processing",
    "app/frontend",
    "app/frontend/static",
    "app/frontend/static/css",
    "app/frontend/static/js",
    "app/frontend/static/img",
    "app/frontend/templates",
    "app/models",
    "app/utils",
    "app/ai",
    "data",
    "data/attachments",
    "data/bodies",
    "data/html_objects",
    "data/emails",
    "data/threads",
    "data/disclaimers",
    "config",
    "logs",
    "tests"
]

# File sections to extract from email_org.txt
FILE_SECTIONS = {
    "# REQUIREMENTS.TXT": "requirements.txt",
    "# CONFIG.JSON": "config/config.json",
    "# DATABASE_MODELS.PY": "app/models/database_models.py",
    "# EMAIL_PROCESSOR.PY": "app/email_processing/email_processor.py",
    "# EMAIL_RETRIEVER.PY": "app/email_processing/email_retriever.py",
    "# ATTACHMENT_HANDLER.PY": "app/email_processing/attachment_handler.py",
    "# HTML_PROCESSOR.PY": "app/email_processing/html_processor.py",
    "# THREAD_MANAGER.PY": "app/email_processing/thread_manager.py",
    "# DATABASE_MANAGER.PY": "app/database/database_manager.py",
    "# EMAIL_PARSER.PY": "app/email_processing/email_parser.py",
    "# SEARCH_ENGINE.PY": "app/utils/search_engine.py",
    "# RULE_ENGINE.PY": "app/utils/rule_engine.py",
    "# CATEGORY_MANAGER.PY": "app/utils/category_manager.py",
    "# AUTH_MANAGER.PY": "app/auth/auth_manager.py",
    "# API_ROUTES.PY": "app/api/routes.py",
    "# APP.PY": "app.py",
    "# AI_ASSISTANT.PY": "app/ai/assistant.py",
    "# UTILS.PY": "app/utils/utils.py",
    "# INDEX.HTML": "app/frontend/templates/index.html",
    "# STYLE.CSS": "app/frontend/static/css/style.css",
    "# MAIN.JS": "app/frontend/static/js/main.js",
    "# README.MD": "README.md",
    "# INIT_DB.PY": "app/database/init_db.py",
    "# INIT_APP.PY": "app/init_app.py"
}

def create_directory_structure(base_dir):
    """Create the directory structure for the application."""
    print("\nCreating directory structure...")
    for directory in DIRECTORIES:
        dir_path = base_dir / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"Created directory: {dir_path}")

def extract_file_sections(base_dir):
    """Extract file sections from email_org.txt."""
    print("\nExtracting file sections from email_org.txt...")
    email_org_path = base_dir / "email_org.txt"
    
    if not email_org_path.exists():
        print(f"Error: {email_org_path} not found.")
        return {}
    
    with open(email_org_path, "r") as f:
        content = f.read()
    
    sections = {}
    for section_name, file_path in FILE_SECTIONS.items():
        pattern = f"{section_name}(.*?)(?=# [A-Z_]+\\.(?:PY|TXT|JSON|HTML|CSS|JS|MD)|$)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sections[file_path] = match.group(1).strip()
        else:
            print(f"Warning: Section {section_name} not found in {email_org_path}")
    
    return sections

def write_files(base_dir, sections):
    """Write extracted sections to files."""
    print("\nWriting extracted files...")
    for file_path, content in sections.items():
        full_path = base_dir / file_path
        
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w") as f:
            f.write(content)
        print(f"Created file: {full_path}")

def setup_virtual_environment(base_dir):
    """Set up a virtual environment and install required packages."""
    print("\nSetting up virtual environment...")
    venv_dir = base_dir / "venv"
    
    # Create virtual environment
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return False
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / "Scripts" / "pip"
    else:  # Unix/Linux/Mac
        pip_path = venv_dir / "bin" / "pip"
    
    # Upgrade pip
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading pip: {e}")
        # Continue anyway
    
    # Install wheel first to help with binary packages
    try:
        subprocess.run([str(pip_path), "install", "wheel"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing wheel: {e}")
        # Continue anyway
    
    # Install required packages
    requirements_file = base_dir / "requirements.txt"
    if requirements_file.exists():
        print("Installing required packages...")
        try:
            # Install packages that don't require compilation first
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=False)
            
            # Check if lxml is commented out in requirements.txt and try to install it separately
            with open(requirements_file, 'r') as f:
                if '# lxml' in f.read():
                    print("Attempting to install lxml separately...")
                    try:
                        subprocess.run([str(pip_path), "install", "lxml==4.6.3"], check=False)
                        print("Successfully installed lxml")
                    except subprocess.CalledProcessError as e:
                        print(f"Warning: Could not install lxml. You may need to install system dependencies: {e}")
                        print("On Debian/Ubuntu: sudo apt-get install libxml2-dev libxslt1-dev python3-dev")
                        print("On Red Hat/CentOS: sudo yum install libxml2-devel libxslt-devel python3-devel")
                        print("On macOS: brew install libxml2 libxslt")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Warning: Some packages could not be installed: {e}")
            print("You may need to install system dependencies for certain packages.")
            print("For lxml: libxml2-dev and libxslt1-dev")
            print("For Pillow: libjpeg-dev, zlib1g-dev, and libpng-dev")
            print("Please see the README.md for more information.")
            return False
    else:
        print(f"Warning: {requirements_file} not found.")
        return False

def main():
    """Main function to set up the Email Organization Application."""
    print("Starting Email Organization Application Setup...")
    
    # Create directory structure
    create_directory_structure(BASE_DIR)
    
    # Extract file sections
    sections = extract_file_sections(BASE_DIR)
    
    # Write files
    write_files(BASE_DIR, sections)
    
    # Set up virtual environment
    print("\nSetting up virtual environment...")
    setup_virtual_environment(BASE_DIR)
    
    print("\nSetup completed!")
    print("To activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print(f"    {BASE_DIR}\\venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print(f"    source {BASE_DIR}/venv/bin/activate")
    print("\nTo run the application:")
    print(f"    python {BASE_DIR}/app.py")

if __name__ == "__main__":
    main()
