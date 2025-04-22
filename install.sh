#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

echo -e "${GREEN}Starting installation process...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    handle_error "Python 3 is not installed. Please install Python 3 and try again."
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    handle_error "requirements.txt not found in the current directory."
fi

# Backend setup
echo -e "${GREEN}Setting up backend...${NC}"

# Create virtual environment
if ! python3 -m venv venv; then
    handle_error "Failed to create virtual environment."
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    handle_error "Could not find virtual environment activation script."
fi

# Install requirements
if ! pip install -r requirements.txt; then
    handle_error "Failed to install requirements."
fi

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}To start the development environment:${NC}"
echo "1. Start the backend:"
echo "   source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate"
echo "   python -m src.main"

exit 0 