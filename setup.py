"""
Setup configuration for the monitors package.
"""

# pylint: disable=import-error
from setuptools import setup, find_packages

setup(
    name="monitors",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.23",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=0.19.0",
        "pillow>=10.0.0",
        "psycopg2-binary>=2.9.1",
        "pytest>=7.0.0",
        "httpx>=0.24.0",
    ],
)
