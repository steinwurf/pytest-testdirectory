import os
import io
from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, 'README.rst'), encoding='utf-8') as fd:
    long_description = fd.read()

setup(
    name='pytest-testdirectory',
    version='1.0.0',
    description=('A py.test plugin providing temporary directories in '
                 'unit tests.'),
    long_description=long_description,
    url='https://github.com/steinwurf/pytest-testdirectory',
    author='Steinwurf ApS',
    author_email='contact@steinwurf.com',
    license='BSD 3-clause "New" or "Revised" License',
    classifiers=[
        'Framework :: Pytest'
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],
    keywords=('pytest py.test '
              'testing unit tests plugin'),
    packages=find_packages(where='src', exclude=['test']),
    install_requires=['pytest'],
    entry_points={
        'pytest11': ['testdirectory = src.testdirectory'],
    },
)
