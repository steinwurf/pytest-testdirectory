#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import shutil
import hashlib
import subprocess

from waflib.Configure import conf
from waflib import Logs

import waflib

top = '.'

VERSION = '1.0.2'

from waflib.Build import BuildContext
class UploadContext(BuildContext):
        cmd = 'upload'
        fun = 'upload'


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
        '--pytest_basetemp', default='pytest_temp',
        help='Set the basetemp folder where pytest executes the tests')


class VirtualEnv(object):

    def __init__(self, cwd, path, ctx):
        """
        Wraps a created virtualenv
        """

        self.path = path
        self.cwd = cwd
        self.ctx = ctx

        self.env = dict(os.environ)

        if 'PATH' in self.env:
            del self.env['PATH']

        if 'PYTHONPATH' in self.env:
            del self.env['PYTHONPATH']

        self.env['PATH'] = os.path.join(path, 'Scripts')

        if sys.platform == 'win32':
            self.env['PATH'] = os.path.join(path, 'Scripts')
        else:
            self.env['PATH'] = os.path.join(path, 'bin')

    def run(self, cmd):
        """ Runs a command in the virtualenv. """
        ret = self.ctx.exec_command(cmd, cwd=self.cwd, env=self.env,
            stdout=None, stderr=None)

        if ret != 0:
            self.ctx.fatal('Exec command failed!')

    def pip_download(self, path, packages):
        """ Downloads a set of packages from pip.

        :param path: The path where the packages should be stored as a string
        :param packages: A list of package names as string, which should be
            downloaded.
        """
        packages = " ".join(packages)

        self.run('python -m pip download {} --dest {}'.format(packages, path))

    def pip_local_install(self, path, packages):
        """ Installs a set of packages from pip, using local packages from the
        path directory.

        :param path: The path where the packages are stored as a string
        :param packages: A list of package names as string, which should be
            downloaded.
        """
        packages = " ".join(packages)

        self.run('python -m pip install --no-index --find-links={} {}'.format(
            path, packages))


    def __enter__(self):
        """ When used in a with statement the virtualenv will be automatically
        revmoved.
        """
        return self

    def __exit__(self, type, value, traceback):
        """ Remove the virtualenv. """
        waflib.extras.wurf.directory.remove_directory(path=self.path)

    @staticmethod
    def create(cwd, name, ctx):
        """ Create a new virtual env.

        :param cwd: The working directory, as a string, where the virtualenv
            will be created and where the commands will run.
        :param name: The name of the virtualenv, as a string. If None a default
            name will be used.
        :param ctx: The Waf Context used to run commands.
        """

        # Make sure the virtualenv Python module is in path
        venv_path = ctx.dependency_path('virtualenv')

        env = dict(os.environ)
        env.update({'PYTHONPATH': os.path.pathsep.join([venv_path])})

        # The Python executable
        python = sys.executable

        if not name:

            # Make a unique virtualenv for different Python executables (e.g. 2.x
            # and 3.x)
            unique = hashlib.sha1(python.encode('utf-8')).hexdigest()[:6]
            name = 'virtualenv-{}'.format(unique)

        # If a virtualenv already exists - lets remove it
        path = os.path.join(cwd, name)
        if os.path.isdir(path):
            waflib.extras.wurf.directory.remove_directory(path=path)

        # Create the new virtualenv
        ctx.cmd_and_log(python+' -m virtualenv ' + name + ' --no-site-packages --clear',
            cwd=cwd, env=env)

        return VirtualEnv(path=path, cwd=cwd, ctx=ctx)


def configure(conf):

    venv = VirtualEnv.create(cwd=conf.path.abspath(), name=None, ctx=conf)

    with venv:

        pip_packages = conf.path.make_node('pip_packages')
        pip_packages.mkdir()

        venv.pip_download(path=pip_packages.abspath(),
            packages=['pytest', 'twine', 'wheel'])


def build(bld):

    # Create a virtualenv in the source folder and build universal wheel
    venv = VirtualEnv.create(cwd=bld.path.abspath(), name=None, ctx=bld)

    with venv:
        pip_packages = bld.path.find_node('pip_packages')

        venv.pip_local_install(path=pip_packages.abspath(), packages=['wheel'])
        venv.run('python setup.py bdist_wheel --universal')

    # Delete the egg-info directory, do not understand why this is created
    # when we build a wheel. But, it is - perhaps in the future there will
    # be some way to disable its creation.
    egg_info = os.path.join(bld.path.abspath(), 'pytest_testdirectory.egg-info')

    if os.path.isdir(egg_info):
        waflib.extras.wurf.directory.remove_directory(path=egg_info)

    # Run the unit-tests
    if bld.options.run_tests:
        _pytest(bld=bld)


def _find_wheel(ctx):
    """ Find the .whl file in the dist folder. """

    wheel = ctx.path.ant_glob('dist/*-'+VERSION+'-*.whl')

    if not len(wheel) == 1:
        ctx.fatal('No wheel found (or version mismatch)')
    else:
        wheel = wheel[0]
        Logs.info('Wheel %s', wheel)
        return wheel


def upload(bld):
    """ Upload the built wheel to PyPI (the Python Package Index) """

    venv = VirtualEnv.create(cwd=bld.bldnode.abspath(), name=None, ctx=bld)

    with venv:
        pip_packages = bld.path.find_node('pip_packages')
        venv.pip_local_install(path=pip_packages.abspath(),
            packages=['twine'])

        wheel = _find_wheel(ctx=bld)

        venv.run('python -m twine upload {}'.format(wheel))


def _pytest(bld):

    # Create the virtualenv in the build folder to make sure we run
    # isolated from the sources
    venv = VirtualEnv.create(cwd=bld.bldnode.abspath(), name=None, ctx=bld)

    with venv:
        pip_packages = bld.path.find_node('pip_packages')
        venv.pip_local_install(path=pip_packages.abspath(),
            packages=['pytest'])

        # Install the pytest-testdirectory plugin in the virtualenv
        wheel = _find_wheel(ctx=bld)

        venv.run('python -m pip install {}'.format(wheel))

        # We override the pytest temp folder with the basetemp option,
        # so the test folders will be available at the specified location
        # on all platforms. The default location is the "pytest" local folder.
        basetemp = os.path.abspath(os.path.expanduser(
            bld.options.pytest_basetemp))

        # We need to manually remove the previously created basetemp folder,
        # because pytest uses os.listdir in the removal process, and that fails
        # if there are any broken symlinks in that folder.
        if os.path.exists(basetemp):
            waflib.extras.wurf.directory.remove_directory(path=basetemp)

        testdir = bld.path.find_node('test')

        # Make python not write any .pyc files. These may linger around
        # in the file system and make some tests pass although their .py
        # counter-part has been e.g. deleted
        venv.run('python -B -m pytest {} --basetemp {}'.format(
            testdir.abspath(), basetemp))
