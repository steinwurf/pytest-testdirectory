============
Introduction
============

Testing code by invoking executable which potentially creates and deletes
files and directories can be hard and error prone.

The purpose of this module is to simplify this task.

pytest-testdirectory provides a py.test fixture for working with temporary
directories.

.. contents:: Table of Contents:
   :local:

Installation
===========

To install pytest-testdirectory::

    pip install pytest-testdirectory

Usage
=====

To make it easy to use in with py.test the TestDirectory object can be
injected into a test function by using the testdirectory fixture.

Example::

    def test_this_function(testdirectory):
        images = testdirectory.mkdir('images')
        images.copy_files('test/images/*')

        r = testdirectory.run('imagecompress --path=images')

        # r is an RunResult object containing information about the command
        # we just executed
        assert r.stdout.match('*finished successfully*')

The testdirectory is an instance of TestDirectory and represents an actual
temporary directory somewhere on the machine running the test code. Using
the API we can create additional temporary directories, populate them with
an initial set of files and finally run some executable and observe its
behavior.

Source code
===========

The main functionality is found in ``src/testdirectory.py`` and the
corresponding unit test is in ``test/test_testdirectory.py`` if you
want to play/modify/fix the code this would, in most cases, be the place
to start.

Developer Notes
===============

We try to make our projects as independent as possible of a local system setup.
For example with our native code (C/C++) we compile as much as possible from
source, since this makes us independent of what is currently installed
(libraries etc.) on a specific machine.

To "fetch" sources we use Waf (https://waf.io/) augmented with dependency
resolution capabilities: https://github.com/steinwurf/waf

The goal is to enable a work-flow where running::

    ./waf configure
    ./waf build --run_tests

Configures, builds and runs any available tests for a given project, such that
you as a developer can start hacking at the code.

For Python project this is a bit unconventional, but we think it works well.

Tests
=====

The tests will run automatically by passing ``--run_tests`` to waf::

    ./waf --run_tests

This follows what seems to be "best practice" advise, namely to install the
package in editable mode in a virtualenv.

Notes
=====

* Why use an ``src`` folder (https://hynek.me/articles/testing-packaging/).
  tl;dr you should run your tests in the same environment as your users would
  run your code. So by placing the source files in a non-importable folder you
  avoid accidentally having access to resources not added to the Python
  package your users will install...
* Python packaging guide: https://packaging.python.org/distributing/
