import os
import io
import re
import sys

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, "README.rst"), encoding="utf-8") as fd:
    long_description = fd.read()

with io.open(os.path.join(cwd, "wscript"), encoding="utf-8") as fd:

    VERSION = None

    regex = re.compile(
        r"""
    (                   # Group and match
        VERSION         #    Match 'VERSION'
        \s*             #    Match zero or more spaces
        =               #    Match and equal sign
        \s*             #    Match zero or more spaces
    )                   # End group

    "                   # Match "
    (                   # Group and match
         \d+\.\d+\.\d+  #    Match digit(s).digit(s).digit(s) e.g. 10.2.3
    )                   # End of group
    "                   # Match "
    """,
        re.VERBOSE,
    )

    for line in fd:

        match = regex.match(line)
        if not match:
            continue

        # The second parenthesized subgroup.
        VERSION = match.group(2)
        break

    else:
        sys.exit("No VERSION variable defined in wscript - aborting!")

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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
    ],
    keywords=("pytest py.test " "testing unit tests plugin"),
    packages=find_packages(where="src", exclude=["test"]),
    package_dir={"": "src"},
    setup_requires=[
        "pytest",
        "setuptools_scm",
        "pytest-runner",
    ],
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
