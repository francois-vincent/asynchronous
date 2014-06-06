# -*- coding: utf-8 -*-

import time
from twisted.internet import reactor, protocol

PORT = 8888


class Echo(protocol.Protocol):
    """This is just about the simplest possible protocol"""

    def dataReceived(self, data):
        request = ''.join((c for c in data if c >= ' '))
        clock = time.strftime("%X")
        print '%s received : <%s>' % (clock, request)

        with open('ack', 'rb') as f:
            response = f.read().strip()
        response = b'\x02' + request[:4] + response + '\x03'
        print '%s send back: <%s>\n' % (clock, response)
        self.transport.write(response)


def main():
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    print '\nServer listening on port %s. Ctrl-C to halt.\n' % PORT
    reactor.listenTCP(PORT, factory)
    reactor.run()

if __name__ == '__main__':
    main()
