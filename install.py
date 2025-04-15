#!/usr/bin/env python3
"""
Helper script to install the robot package properly.
This ensures the controller factory and other modules can be imported.
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Install the robot package in development mode."""
    print("Installing the robot package...")
    
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.absolute()
    
    # Change to the project root
    os.chdir(project_root)
    
    # Install the package in development mode
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("\nSuccess! The robot package has been installed in development mode.")
        print("You can now import it from anywhere on your system.")
        print("\nTry running 'start.py' to test the robot controller.")
    except subprocess.CalledProcessError as e:
        print(f"\nError: Failed to install the package: {e}")
        print("Please install the package manually with 'pip install -e .'")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 