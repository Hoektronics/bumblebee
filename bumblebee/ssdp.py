import sys
from botqueueapi import getLocalIPAddress
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900

MS = 'M-SEARCH * HTTP/1.1\r\n'
MS+= 'HOST: %s:%d\r\n' % (SSDP_ADDR, SSDP_PORT)
MS+= 'MAN: "ssdp:discover"\r\n'
MS+= 'MX: 2\r\n'
MS+= 'ST: ssdp:all\r\n\r\n'

class SSDPClient(DatagramProtocol):
  def __init__(self, iface):
    self.iface = iface
    self.ssdp = reactor.listenMulticast(SSDP_PORT, self, listenMultiple=True)
    self.ssdp.setLoopbackMode(1)
    self.ssdp.joinGroup(SSDP_ADDR, interface=iface)

  def datagramReceived(self, datagram, address):
    print "DATAGRAM START"
    print datagram
    print "DATAGRAM END"
    print ""

  def stop(self):
    self.ssdp.leaveGroup(SSDP_ADDR, interface=iface)
    self.ssdp.stopListening()

def main(iface):
  client = SSDPClient(iface)
  reactor.addSystemEventTrigger('before', 'shutdown', client.stop)

if __name__ == "__main__":
  iface = getLocalIPAddress()
  if iface is None:
    print "Could not get local IP address"
    sys.exit(1)
  print "My IP address is %s" % iface
  reactor.callWhenRunning(main, iface)
  reactor.run()
