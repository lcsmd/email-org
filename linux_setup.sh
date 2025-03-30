#!/bin/bash

# Email Organization Application Linux Setup Script
# This script installs system dependencies and sets up the application

echo "Starting Email Organization Application Linux Setup..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run parts of this script with sudo when prompted"
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
  python3-dev \
  python3-pip \
  python3-venv \
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

# Setup virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "Installing Python packages..."
pip install wheel  # Install wheel first to help with binary packages
pip install -r requirements.txt

# Now install lxml separately since system dependencies are installed
echo "Installing lxml..."
pip install lxml==4.6.3

# Run the Python setup script if it exists
if [ -f "setup.py" ]; then
  echo "Running Python setup script..."
  python setup.py
fi

echo "Setup completed successfully!"
echo "To activate the virtual environment, run: source venv/bin/activate"
