#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting installation process...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Backend setup
echo -e "${GREEN}Setting up backend...${NC}"
python3 -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
echo -e "${GREEN}Setting up frontend...${NC}"
cd frontend
npm install
cd ..

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}To start the development environment:${NC}"
echo "1. Start the backend:"
echo "   source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate"
echo "   python -m src.main"
echo "2. Start the frontend:"
echo "   cd frontend"
echo "   npm run dev" 