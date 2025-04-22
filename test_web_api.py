#!/usr/bin/env python3
"""
Test script for the robot web API
"""
import requests
import json
import time
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_api(base_url="http://localhost:5000"):
    """Test the robot web API endpoints"""
    
    print(f"Testing robot web API at {base_url}")
    
    # Test the init endpoint
    print("\n1. Testing /api/init endpoint...")
    try:
        response = requests.post(f"{base_url}/api/init")
        if response.status_code == 200:
            print(f"✓ SUCCESS: {response.json()}")
        else:
            print(f"✗ ERROR: Status code {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        print("  Make sure the web server is running")
        return
    
    # Test the servo endpoint
    print("\n2. Testing /api/servo endpoint...")
    try:
        data = {
            "servo_id": 0,  # Head servo
            "angle": 90,    # Center position
            "speed": 0.01   # Movement speed
        }
        response = requests.post(
            f"{base_url}/api/servo",
            json=data
        )
        if response.status_code == 200:
            print(f"✓ SUCCESS: {response.json()}")
        else:
            print(f"✗ ERROR: Status code {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return
    
    # Test the robot_info endpoint
    print("\n3. Testing /api/robot_info endpoint...")
    try:
        response = requests.get(f"{base_url}/api/robot_info")
        if response.status_code == 200:
            print(f"✓ SUCCESS: Robot info retrieved")
            info = response.json()
            print(f"  Robot initialized: {info['data']['initialized']}")
            print(f"  Using mock mode: {info['data']['using_mock']}")
        else:
            print(f"✗ ERROR: Status code {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return
        
    print("\n=== API Test Complete ===")
    
if __name__ == "__main__":
    # Use command line argument for base URL if provided
    if len(sys.argv) > 1:
        test_api(sys.argv[1])
    else:
        test_api() 