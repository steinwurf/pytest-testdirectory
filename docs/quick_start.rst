Quick Start
===========

The following section will help you get started.

The fastest way to get started is to ``pip install`` the package::

    python3 -m pip install dummynet

After this you are ready to go::

   import logging
   import dummynet

   log = logging.getLogger("dummynet")
   log.setLevel(logging.DEBUG)

   process_monitor = dummynet.ProcessMonitor(log=log)

   shell = dummynet.HostShell(log=log, sudo=sudo, process_monitor=process_monitor)

   net = dummynet.DummyNet(shell=shell)

   try:

      # Get a list of the current namespaces
      namespaces = net.netns_list()
      assert namespaces == []

      # create two namespaces
      demo0 = net.netns_add(name="demo0")
      demo1 = net.netns_add(name="demo1")

      net.link_veth_add(p1_name="demo0-eth0", p2_name="demo1-eth0")

      # Move the interfaces to the namespaces
      net.link_set(namespace="demo0", interface="demo0-eth0")
      net.link_set(namespace="demo1", interface="demo1-eth0")

      # Bind an IP-address to the two peers in the link.
      demo0.addr_add(ip="10.0.0.1/24", interface="demo0-eth0")
      demo1.addr_add(ip="10.0.0.2/24", interface="demo1-eth0")

      # Activate the interfaces.
      demo0.up(interface="demo0-eth0")
      demo1.up(interface="demo1-eth0")
      demo0.up(interface="lo")
      demo1.up(interface="lo")

      # Test will run until last non-daemon process is done.
      proc0 = demo0.run_async(cmd="ping -c 20 10.0.0.2", daemon=True)
      proc1 = demo1.run_async(cmd="ping -c 10 10.0.0.1")

      # Print output as we go (optional)
      def _proc0_stdout(data):
         print("proc0: {}".format(data))

      def _proc1_stdout(data):
         print("proc1: {}".format(data))

      proc0.stdout_callback = _proc0_stdout
      proc1.stdout_callback = _proc1_stdout

      while process_monitor.run():
         pass

      # Check that the ping succeeded.
      proc1.match(stdout="10 packets transmitted*", stderr=None)

      # Since proc0 is a daemon we automatically kill it when the last
      # non-daemon process is done. However we can still see the output it
      # generated.
      print(f"proc0: {proc0.stdout}")

   finally:

      # Clean up.
      net.cleanup()