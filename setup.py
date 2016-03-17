import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(
    # Application name:
    name="HypercatBuilder",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Thingful",
    author_email="marco@thingful.net",

    # Packages
    packages=["hypercat-builder"],

    include_package_data=False,

    install_requires=['docopt', 'hypercat.py'],

    # Details
    url="http://pypi.python.org/pypi/MyApplication_v010/",

    # License
    license='MIT',

    # Description
    description="Simple script to build Transport API hypercat catalogues",

    # long_description
    long_description= README,

    # Dependent packages (distributions)
    keywords='development hypercat',
)