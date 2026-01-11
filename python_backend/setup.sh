#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

echo "Setup complete! Run 'source venv/bin/activate' and then 'python server.py' to start the server."
