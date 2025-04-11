from setuptools import setup, find_packages

setup(
    name="robot_controller",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Adafruit-PCA9685",
    ],
    python_requires=">=3.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="A controller for a humanoid robot using PCA9685 servo controller",
    long_description=open("README.md").read() if open("README.md").read() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/robot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 