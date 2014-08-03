# -*- coding: utf-8 -*-

import itertools
import time
from twisted.internet import reactor, protocol

PORT = 8888


class Echo(protocol.Protocol):
    """ A server protocol designed to debug JBT-ACI client
        1- responds to HeartBeat messages.
        2- sends periodic messages.
        All messages (HeartBeat ack or sent messages) are contained
        in files and can be changed on the fly.
    """

    def get_message(self, source, prefix):
        try:
            with open(source, 'rb') as f:
                response = f.read().strip()
        except Exception:
            print "  ERROR Can't find file <%s>" % source
            response = '[MessageType]Unknown|'
        if not '[MessageType]' in response:
            print "  ERROR Empty file <%s>" % source
            response = '[MessageType]Unknown|'
        return b'\x02' + prefix + response + '\x03'

    def send_message(self, message, legend="send message"):
        clock = time.strftime("%X")
        print '  %s %s: <%s>\n' % (clock, legend, message)
        self.transport.write(message)

    def sendPeriodicMessage(self):
        period_iterator = itertools.cycle((10, 40))
        period = lambda: next(period_iterator)
        message_iterator = itertools.cycle(('drop_cart', 'cart_removed'))
        message = lambda: next(message_iterator)
        def send(filename):
            if not self.connected:
                return
            data = self.get_message(filename, '00%02d' % next(self.count))
            self.send_message(data)
            reactor.callLater(period(), send, message())
        reactor.callLater(period(), send, message())

    def connectionMade(self):
        self.connected = True
        self.count = itertools.count(1)
        print "\nConnection established.\n"
        self.sendPeriodicMessage()

    def connectionLost(self, reason=protocol.connectionDone):
        self.connected = False
        print "\nConnection lost: %s.\n" % reason

    def dataReceived(self, data):
        request = ''.join((c for c in data if c >= ' '))
        clock = time.strftime("%X")
        print '  %s received : <%s>' % (clock, request)

        if 'HeartBeat' in request:
            response = self.get_message('ack', request[:4])
            self.send_message(response, legend='send back')


def main():
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    print '\nServer started at %s, listening on port %s. Ctrl-C to quit.\n' % (time.strftime("%X"), PORT)
    reactor.listenTCP(PORT, factory)
    reactor.run()

if __name__ == '__main__':
    main()
