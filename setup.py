import os
from importlib import import_module
from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    return import_module("whispers.__version__").__version__


install_requires = ["luhn==0.2.0", "lxml==4.6.2", "pyyaml==5.3.1", "astroid==2.4.2", "jproperties==2.1.0", "python-levenshtein==0.12.0"]

dev_requires = [
    "black>=19.10b0",
    "coverage~=4.4",
    "coverage-badge>=1.0.1",
    "flake8>=3.8.1",
    "isort>=4.3.21",
    "pytest>=2.9.1",
    "pytest-mock>=1.0",
    "pip-tools>=4.4.1",
    "wheel>=0.34.2",
    "twine>=3.1.1",
]

setup(
    name="whispers",
    version=get_version(),
    url="https://github.com/Skyscanner/whispers",
    author="Artëm Tsvetkov",
    author_email="artem.tsvetkov@skyscanner.net",
    description="Identify secrets and dangerous behaviours",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=install_requires,
    setup_requires=["pytest-runner"],
    tests_require=dev_requires,
    extras_require={"dev": dev_requires},
    entry_points={"console_scripts": ["whispers=whispers.cli:cli"]},
)
