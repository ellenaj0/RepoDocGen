"""
Setup script for RepoDocGen
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="repodocgen",
    version="0.1.0",
    author="Ellena Jiang, Aryaman Velampalli, Chengtao Dai",
    description="LLM-powered repository documentation generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ellenaj0/RepoDocGen",
    packages=find_packages(exclude=["tests", "benchmarks", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "repodocgen=main:main",
        ],
    },
    include_package_data=True,
    keywords="code documentation llm gemini repository analysis",
)
