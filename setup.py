import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    # Application name:
    name="HypercatBuilder",

    # Version number (initial):
    version="0.1.2",

    # Application author details:
    author="Thingful",
    author_email="marco@thingful.net",

    # Packages
    packages=["hypercat_builder"],

    include_package_data=False,

    install_requires=['docopt', 'hypercat.py >= 0.1.2'],

    tests_require=['mock', 'nose'],

    test_suite='nose.collector',

    scripts=['bin/hypercat_builder'],

    # Details
    url="https://bitbucket.org/thingful/hypercat-builder",

    # License
    license='MIT',

    # Description
    description="Simple tool to build Transport API Hypercat catalogues",

    # long_description
    long_description= README,

    # Dependent packages (distributions)
    keywords='development hypercat',
)
