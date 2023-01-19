Welcome to DummyNet's documentation!
====================================

A Python based light-weight network testing tool using network namespaces.

DummyNet is a tool for working local test networks in Python on a Linux
machine. By using a virtual network namespace, it is possible to create
virtual network interfaces and to connect them to each other. This allows
you to test your network applications without the need to have a real
network connection.

The class is a Python wrapper for the Linux ``ip netns``
and ``ip link`` tools.

So far, Ubuntu and Debian are supported, but please make sure, that you
have the iproute2 linux-package installed with::

    apt-get install iproute2

Other Linux operating systems have not been tested, but feel free to open an
issue if support is needed.

To get started, please read the :ref:`quick start` section.


.. toctree::
   :maxdepth: 2
   :hidden:

   quick_start
   api/api
   developers
