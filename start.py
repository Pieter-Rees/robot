#!/usr/bin/env python3
"""
Robot Controller Starter Script

This script provides a simple way to start either the robot controller or web interface.
"""

import argparse
import sys
from robot import create_controller, web_app
from robot.config import I2C_CONFIG

def main():
    parser = argparse.ArgumentParser(description='Robot Controller Starter')
    parser.add_argument('--mode', choices=['controller', 'web'], default='controller',
                      help='Mode to start the robot in (default: controller)')
    parser.add_argument('--host', default='0.0.0.0',
                      help='Host to run the web server on (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                      help='Port to run the web server on (default: 5000)')
    
    args = parser.parse_args()
    
    if args.mode == 'controller':
        try:
            controller = create_controller(I2C_CONFIG)
            print("Starting robot controller...")
            # Add your controller initialization and main loop here
            # For example:
            # controller.initialize()
            # controller.run()
        except Exception as e:
            print(f"Error starting controller: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            print(f"Starting web interface on {args.host}:{args.port}...")
            web_app.run(host=args.host, port=args.port)
        except Exception as e:
            print(f"Error starting web interface: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main() 