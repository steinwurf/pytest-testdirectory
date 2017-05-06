============
Introduction
============

pytest-testdirectory provides a pytest fixture for working with temporary
directories.

.. contents:: Table of Contents:
   :local:



Tests
=====

It seems that "best practice" advise is to install the package in editable
mode::

    pip install . -e

Although it does not seem to be explicitly mentioned anywhere, best practice
should also be to do this in a ``virtualenv``?

This would require that the ``virtualenv`` tool is available on the buildslaves. (
I'm not sure what) is the status there? In particular on the Windows slaves.

testing (such)

We setup the tests as described here:
http://stackoverflow.com/q/20971619/1717320



Run the tests::

    pytest test


Related plugins
===============



Notes
=====

* Why use an ``src`` folder (https://hynek.me/articles/testing-packaging/).
  tl;dr you should run your tests in the same environment as your users would
  run your code. So by placing the source files in a non-importable folder you
  avoid accidentally having access to resources not added to the Python
  package your users will install...
* Python packaging guide: https://packaging.python.org/distributing/
