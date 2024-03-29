import os
import io
import re
import sys

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, "README.rst"), encoding="utf-8") as fd:
    long_description = fd.read()

VERSION = "5.0.0"

setup(
    name="pytest-testdirectory",
    version=VERSION,
    description=("A py.test plugin providing temporary directories in " "unit tests."),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/steinwurf/pytest-testdirectory",
    author="Steinwurf ApS",
    author_email="contact@steinwurf.com",
    license='BSD 3-clause "New" or "Revised" License',
    classifiers=[
        "Framework :: Pytest",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
    keywords=("pytest py.test " "testing unit tests plugin"),
    packages=find_packages(where="src", exclude=["test"]),
    package_dir={"": "src"},
    setup_requires=["pytest"],
    install_requires=[
        "pytest",
    ],
    tests_require=[
        "pytest",
    ],
    entry_points={
        "pytest11": ["testdirectory = pytest_testdirectory.testdirectory"],
    },
)
