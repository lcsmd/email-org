#!/bin/bash

# Email Organization Application Miniconda Setup Script
# This script installs system dependencies and sets up the application for Miniconda environments

echo "Starting Email Organization Application Miniconda Setup..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run parts of this script with sudo when prompted"
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
  python3-dev \
  libxml2-dev \
  libxslt1-dev \
  zlib1g-dev \
  libjpeg-dev \
  libpng-dev \
  libffi-dev \
  libssl-dev

# Create directory structure if not already created
echo "Creating directory structure if needed..."
mkdir -p app/api
mkdir -p app/auth
mkdir -p app/database
mkdir -p app/email_processing
mkdir -p app/frontend/static/css
mkdir -p app/frontend/static/js
mkdir -p app/frontend/static/img
mkdir -p app/frontend/templates
mkdir -p app/models
mkdir -p app/utils
mkdir -p app/ai
mkdir -p data/attachments
mkdir -p data/bodies
mkdir -p data/html_objects
mkdir -p data/emails
mkdir -p data/threads
mkdir -p data/disclaimers
mkdir -p config
mkdir -p logs
mkdir -p tests

# Create a dedicated conda environment
echo "Setting up conda environment..."
conda create -y -n email-org python=3.10
echo "Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate email-org

# Install Python packages using conda first for packages with C dependencies
echo "Installing packages with conda..."
conda install -y -c conda-forge lxml beautifulsoup4 pillow cryptography

# Install remaining packages with pip
echo "Installing remaining packages with pip..."
pip install flask==2.0.1 flask-restful==0.3.9 flask-cors==3.0.10 flask-jwt-extended==4.3.1 flask-sqlalchemy==2.5.1
pip install werkzeug==2.0.1 sqlalchemy==1.4.23 pyjwt==2.1.0 bcrypt==3.2.0 python-dotenv==0.19.0
pip install exchangelib==4.6.2 google-api-python-client==2.19.0 google-auth-oauthlib==0.4.6
pip install html2text==2020.1.16 chardet==4.0.0 python-magic==0.4.24
pip install requests==2.26.0 python-dateutil==2.8.2 pytz==2021.1 uuid==1.30
pip install openai==0.27.0 pytest==6.2.5 black==21.8b0 flake8==3.9.2

# Run the Python setup script if it exists
if [ -f "setup.py" ]; then
  echo "Running Python setup script..."
  python setup.py
fi

echo "Setup completed successfully!"
echo "To activate the conda environment, run: conda activate email-org"
