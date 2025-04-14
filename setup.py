#!/usr/bin/env python3
"""
Setup script for the humanoid robot project.
This enables the robot package to be installed with pip.
"""
import os
from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = []
    for line in f:
        # Skip comments and empty lines
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

# Read README.md for the long description
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="humanoid-robot",
    version="1.0.0",
    description="Control system for a humanoid robot using Raspberry Pi and PCA9685",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Robot Team",
    author_email="robot@example.com",
    url="https://github.com/example/robot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'robot=robot:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="robot, raspberry pi, servo, humanoid, education",
) 