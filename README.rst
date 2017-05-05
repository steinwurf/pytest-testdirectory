============
Introduction
============

pytest-testdirectory provides a pytest fixture for working with temporary
directories.

.. contents:: Table of Contents:
   :local:



Tests
=====

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
