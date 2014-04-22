# -*- coding: utf-8 -*-

from tornado import websocket, web, ioloop

cl = []
broadcast = True


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class SocketHandler(websocket.WebSocketHandler):

    def open(self):
        if self not in cl:
            print("New connection (%s total)" % len(cl))
            cl.append(self)

    def on_message(self, message):
        print("received message <%s>" % message)
        if broadcast:
            for ws in cl:
                ws.write_message(message)
        else:
            self.write_message(message)

    def on_close(self):
        if self in cl:
            cl.remove(self)

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
])

if __name__ == '__main__':
    app.listen(8080)
    ioloop.IOLoop.instance().start()
