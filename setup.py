from setuptools import setup, find_packages
import io

# Read the README.md file with proper encoding
with io.open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="robot-controller",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "adafruit-circuitpython-pca9685==3.3.9",
        "adafruit-circuitpython-servokit==1.3.15",
        "RPi.GPIO==0.7.1",
        "flask==2.0.1",
        "Werkzeug==2.0.2",
        "Jinja2==3.0.3",
        "itsdangerous==2.0.1",
        "MarkupSafe==2.0.1",
        "Adafruit-PCA9685>=1.0.1",
        "setuptools>=65.5.1",
    ],
    python_requires=">=3.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python-based controller for a humanoid robot using the PCA9685 servo controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/robot-controller",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "robot-controller=robot.controllers.robot_controller:main",
            "robot-web=robot.web.web_server:main",
        ],
    },
) 