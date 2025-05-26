#!/usr/bin/env python3
"""
Setup script for Accessibility Service
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="accessibility-service",
    version="1.0.0",
    author="Suoke Life Team",
    author_email="dev@suokelife.com",
    description="AI-powered accessibility service for Suoke Life platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suokelife/accessibility-service",
    packages=find_packages(exclude=['tests*', 'test*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'flake8>=4.0.0',
            'mypy>=0.991',
            'pre-commit>=2.20.0',
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.8.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'accessibility-service=cmd.server.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'accessibility_service': [
            'config/*.yaml',
            'config/*.yml',
            'config/*.json',
            'data/*.json',
            'data/*.yaml',
        ],
    },
) 