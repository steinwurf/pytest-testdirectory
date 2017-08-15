News for pytest-testdirectory
=============================

This file lists the major changes between versions. For a more detailed list
of every change, see the Git log.

Latest
------
* tbd

3.1.0
-----
* Minor: Adding support for symlink to directories.

3.0.0
-----
* Minor: Adding support for symlink to files.
* Major: Changed the way the run(...) method of the testdirectory works.
  It no longer implicitly takes a list of arguments, but rather either
  a list or string.

2.1.0
-----
* Patch: Remove VirtualEnv wrapper from wscript. Instead that functionality has
  been moved to Waf.
* Minor: Better handling of keyword arguments to the testdirectory run(...)
  method.

2.0.0
-----
* Minor: Added virtualenv wrapper.
* Major: Fix entry broken entry point. Previous versions where not usable
  when installed via pip.

1.0.2
-----
* Patch: Fail on errors in upload

1.0.1
-----
* Patch: Testing release script

1.0.0
-----
* Major: Initial release
