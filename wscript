#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import shutil
import hashlib

import waflib

top = '.'

def resolve(ctx):

    # Testing dependencies
    ctx.add_dependency(
        name='virtualenv',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='15.1.0',
        sources=['github.com/pypa/virtualenv.git'])


def options(opt):

    opt.add_option(
        '--run_tests', default=False, action='store_true',
        help='Run all unit tests')

    opt.add_option(
        '--pytest_basetemp', default='pytest',
        help='Set the basetemp folder where pytest executes the tests')


def build(bld):

    if bld.options.run_tests:
        _pytest(bld=bld)


def _pytest(bld):

    python_path = \
    [
        bld.dependency_path('virtualenv'),
    ]

    bld_env = bld.env.derive()
    bld_env.env = dict(os.environ)

    separator = ';' if sys.platform == 'win32' else ':'
    bld_env.env.update({'PYTHONPATH': separator.join(python_path)})

    # We use the binaries in the virtualenv
    if sys.platform == 'win32':
        folder = 'Scripts'
        ext = '.exe'
    else:
        folder = 'bin'
        ext = ''

    host_python_binary = sys.executable

    # Make a new virtual env for different host executables
    virtualenv_hash = hashlib.sha1(
        host_python_binary.encode('utf-8')).hexdigest()[:6]

    virtualenv = 'pytest_environment_'+virtualenv_hash
    python_binary = os.path.join(virtualenv, folder, 'python' + ext)
    pip_binary = os.path.join(virtualenv, folder, 'pip' + ext)


    bld(rule=host_python_binary+' -m virtualenv ' + virtualenv + ' --no-site-packages',
        cwd=bld.path,
        env=bld_env,
        always=True)

    bld.add_group()

    bld(rule=python_binary+' -m pip install pytest',
        cwd=bld.path,
        env=bld_env,
        always=True)

    bld.add_group()

    bld(rule=python_binary+' -m pip install . -e',
        cwd=bld.path,
        env=bld_env,
        always=True)

    # We override the pytest temp folder with the basetemp option,
    # so the test folders will be available at the specified location
    # on all platforms. The default location is the "pytest" local folder.
    basetemp = os.path.abspath(os.path.expanduser(bld.options.pytest_basetemp))

    # We need to manually remove the previously created basetemp folder,
    # because pytest uses os.listdir in the removal process, and that fails
    # if there are any broken symlinks in that folder.
    if os.path.exists(basetemp):
        waflib.extras.wurf.directory.remove_directory(path=basetemp)

    # Make python not write any .pyc files. These may linger around
    # in the file system and make some tests pass although their .py
    # counter-part has been e.g. deleted
    command = python_binary + ' -B -m pytest test --basetemp ' + basetemp

    bld(rule=command,
        cwd=bld.path,
        env=bld_env,
        always=True)
