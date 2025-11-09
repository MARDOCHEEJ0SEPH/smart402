"""
Smart402 Python SDK Setup
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smart402",
    version="1.0.0",
    author="Mardochée JOSEPH",
    author_email="developers@smart402.io",
    description="Python SDK for Smart402 - Universal Protocol for AI-Native Smart Contracts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smart402/framework",
    project_urls={
        "Bug Reports": "https://github.com/smart402/framework/issues",
        "Documentation": "https://docs.smart402.io",
        "Source": "https://github.com/smart402/framework/tree/main/sdk/python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart402=smart402.cli.main:main",
        ],
    },
    keywords=[
        "smart402",
        "smart-contracts",
        "blockchain",
        "ai",
        "llm",
        "aeo",
        "llmo",
        "x402",
        "automated-payments",
        "web3",
        "ethereum",
        "polygon",
    ],
    include_package_data=True,
    zip_safe=False,
)
