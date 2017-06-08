News for pytest-testdirectory
=============================

This file lists the major changes between versions. For a more detailed list
of every change, see the Git log.

Latest
------
* Patch: Remove VirtualEnv wrapper from wscript. Instead that functionality has
  been moved to waf.
  Minor: Better handeling of keyword arguments to the testdirectory run(...)
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
