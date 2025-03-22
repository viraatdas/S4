"""Setup script for S4."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="s4-storage",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Smart S3 Storage Service with LLM indexing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/S4",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "s4=s4.__main__:main",
            "s4-cli=s4.cli:main",
        ],
    },
) 