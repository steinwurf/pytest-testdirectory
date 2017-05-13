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
        '--pytest_basetemp', default='pytest',
        help='Set the basetemp folder where pytest executes the tests')


class VirtualEnv(object):

    def __init__(self, path, ctx):
        """
        Wraps a create virtualenv
        """

        self.path = path
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
        """
        """
        self.ctx.cmd_and_log(cmd, env=self.env)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        waflib.extras.wurf.directory.remove_directory(
            path=self.virtualenv.path)

    @staticmethod
    def create(cwd, name, ctx):

        venv_path = ctx.dependency_path('virtualenv')

        env = dict(os.environ)
        env.update({'PYTHONPATH': os.path.pathsep.join(venv_path)})

        # The Python executable
        python = sys.executable

        if not name:

            # Make a unique virtualenv for different Python executables (e.g. 2.x
            # and 3.x)
            unique = hashlib.sha1(python.encode('utf-8')).hexdigest()[:6]
            name = 'virtualenv-{}'.format(unique)

        print('Create virtualenv')

        print("cwd {}".format(cwd))

        ctx.cmd_and_log(python+' -m virtualenv ' + name + ' --no-site-packages',
            cwd=cwd, env=env)

        return VirtualEnv(path=os.path.join(cwd, name), ctx=ctx)

def configure(conf):


    venv = VirtualEnv.create(cwd=conf.path.abspath(), name=None, ctx=conf)

    with venv:

        pip_packages = conf.path.make_node('pip_packages')
        pip_packages.mkdir()

        venv.run('python -c "import sys; print(sys.executable)"')
        venv.run('python -m pip download pytest twine wheel --dest %s' % pip_packages.abspath())



def build(bld):

    if bld.options.run_tests:
        _pytest(bld=bld)

    # Build Universal Wheel
    bld(rule='${VPYTHON} -m pip install wheel',
        cwd=bld.path,
        always=True)

    bld.add_group()

    bld(rule='${VPYTHON} setup.py bdist_wheel --universal',
        cwd=bld.path,
        always=True)


def upload(ctx):

    wheel = ctx.path.ant_glob('dist/*-'+VERSION+'-*.whl')

    if not len(wheel) == 1:
        ctx.fatal('No wheel to upload (or version mismatch)')
    else:
        Logs.info('Wheel %s', wheel[0])

    ctx.cmd_and_log('%s -m pip install twine' % ctx.env.VPYTHON[0], cwd=ctx.path,
        quiet=waflib.Context.BOTH)
    ret = ctx.exec_command('%s -m twine upload %s' % (ctx.env.VPYTHON[0], wheel[0]),
        cwd=ctx.path, stdout=None, stderr=None)

    if ret != 0:
        ctx.fatal('Upload failed!')


def _pytest(bld):


    bld(rule='${VPYTHON} -m pip install pytest',
        cwd=bld.path,
        always=True)

    bld.add_group()

    # Install the pytest-testdirectory plugin in the virtualenv
    bld(rule='${VPYTHON} -m pip install -e .',
        cwd=bld.path,
        always=True)

    bld.add_group()

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
    command = '${VPYTHON} -B -m pytest test --basetemp ' + basetemp

    bld(rule=command,
        cwd=bld.path,
        always=True)

    bld.add_group()
