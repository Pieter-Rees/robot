"""
Web interface package for the humanoid robot.
Provides a Flask-based web server and REST API for robot control.
"""

from .web_server import app

__all__ = ['app'] 