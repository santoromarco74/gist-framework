#!/usr/bin/env python3
"""
GIST Framework Setup
Setup script for installing GIST Framework package
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gist-framework",
    version="1.0.0",
    author="GIST Framework Research Team",
    author_email="gist-framework@research.org",
    description="Framework per la Valutazione della Maturità Digitale nel settore GDO",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/gist-framework",
    project_urls={
        "Documentation": "https://docs.gist-framework.org",
        "Bug Tracker": "https://github.com/your-org/gist-framework/issues",
        "Source Code": "https://github.com/your-org/gist-framework",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=3.0.0",
            "black>=21.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "mkdocs>=1.2.0",
            "mkdocs-material>=7.3.0",
            "mkdocs-mermaid2-plugin>=0.6.0",
        ],
        "viz": [
            "graphviz>=0.17.0",
            "pygraphviz>=1.7.0",
        ],
        "api": [
            "fastapi>=0.70.0",
            "uvicorn>=0.15.0",
            "prometheus-client>=0.12.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipython>=7.25.0",
            "ipywidgets>=7.6.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "gist-calc=gist_calculator:main",
            "assa-calc=assa_gdo_calculator:main",
            "gdo-twin=gdo_digital_twin:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gist_framework": [
            "templates/*.json",
            "templates/*.sh",
            "configs/*.yaml",
            "data/*.csv",
        ],
    },
    keywords=[
        "security",
        "risk-assessment",
        "digital-maturity",
        "gdo",
        "retail",
        "cloud-security",
        "compliance",
        "zero-trust"
    ],
    zip_safe=False,
)