"""Standard setup function for a Python package"""
from setuptools import setup, find_packages

setup(
    name="pycabtech",
    version="0.1.0",
    author="CabTech",
    description="Handy functions",
    packages=find_packages(),
    install_requires=[
        "boto3",
    ],
)
