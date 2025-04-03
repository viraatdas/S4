"""Setup script for S4 - Smart S3 Storage Service."""

import os
from setuptools import setup, find_packages

# Read the long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "S4 - Smart S3 Storage Service"

# Read requirements from requirements.txt
requirements = []
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback requirements if file is not found
    requirements = [
        "boto3>=1.28.0",
        "langchain>=0.0.267",
        "langchain-openai>=0.0.2",
        "fastapi>=0.103.0",
        "uvicorn>=0.23.0",
        "python-dotenv>=1.0.0",
        "python-multipart>=0.0.6",
        "faiss-cpu>=1.7.4",
        "click>=8.1.7",
        "pydantic>=2.3.0",
        "pydantic[email]>=2.3.0",
        "tiktoken>=0.4.0",
        "tenacity>=8.2.3",
        "PyPDF2>=3.0.0",
        "python-docx>=0.8.11"
    ]

setup(
    name="s4-storage",
    version="0.1.0",
    author="S4 Team",
    author_email="example@example.com",
    description="Smart S3 Storage Service with semantic search capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/s4",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "s4=s4.__main__:cli",
            "s4-server=s4.__main__:cli"
        ],
    },
) 