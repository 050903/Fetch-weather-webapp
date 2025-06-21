"""
Setup script for Weather Analytics Dashboard
Author: Tran The Hao
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="weather-analytics-dashboard",
    version="1.0.0",
    author="Tran The Hao",
    author_email="",
    description="A real-time weather data analytics and visualization web application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tranthehao/weather-analytics-dashboard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "weather-dashboard=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["static/*", "templates/*", "database/*"],
    },
    keywords="weather, analytics, dashboard, flask, socketio, realtime, visualization",
    project_urls={
        "Bug Reports": "https://github.com/tranthehao/weather-analytics-dashboard/issues",
        "Source": "https://github.com/tranthehao/weather-analytics-dashboard",
        "Documentation": "https://github.com/tranthehao/weather-analytics-dashboard/blob/main/README.md",
    },
)