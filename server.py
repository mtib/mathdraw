#!/usr/bin/env python3

"""Server side of MathDraw application

should be hosted on $MATHDRAW so the client connects properly
"""

import socket
import os
import sys
import time
from threading import Thread

PORT = 8228
MAX_OFFSET = 100

class MathServer():
    sfile = dict()
    sock = None
    cons = []

    def __init__(self):
        self.debug = "-v" in sys.argv
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        offset = 0
        while True:
            try:
                self.sock.bind(('', PORT + offset))
                break
            except Exception as e:
                print("could not open port {}, trying {} next".format(PORT+offset, PORT+offset+1))
            offset = offset + 1
            if offset > MAX_OFFSET:
                raise(Exception())
        self.sock.listen(0)

    def _debug(self, *st):
        if self.debug:
            print(*st)


    def _accept(self, conn, addr):
        print(" <- started thread for {}".format(addr))
        self.sfile[addr] = conn.makefile()
        self.cons.append((conn, addr))
        conn.send(b'accept\n')
        print(" <- accepted connection for {}".format(addr))
        while self.running:
            msg = 'close'
            try:
                msg = self.sfile[addr].readline()[:-1]
            except ConnectionResetError:
                msg = 'close'
            if len(msg) == 0:
                self._debug("newline received")
                msg = 'close'
            if msg == 'close':
                conn.close()
                self.sfile[addr].close()
                self.cons.remove((conn,addr))
                self.sfile.pop(addr)
                print(" -/-> tcp & file {}".format(addr))
                return
            elif msg[0] == 'd':
                self._debug("draw:", msg.split(":"))
                self._mirror(msg, conn)
            elif msg[0] == 'e':
                self._debug("erase:", msg.split(":"))
                self._mirror(msg, conn)
            elif msg[0] == 't':
                self._debug("text:", msg.split(":"))
                self._mirror(msg, conn)
            elif msg[0] == 'c':
                self._debug("change:", msg.split(":"))
            else:
                self._debug("unknown command \033[35m\"\"\"{}\"\"\"\033[0m by {}".format(msg, addr))

    def _mirror(self, msg, conn):
        for c in self.cons:
            if c[0] != conn:
                c[0].send('{}\n'.format(msg).encode('ascii'))

    def start(self):
        print("starting server")
        while self.running:
            c, a = self.sock.accept()
            print(" -> connection: {}".format(a))
            Thread(target=self._accept, args=[c, a]).start()

    def close(self):
        self.running = False
        for i in self.sfile:
            print(" -/-> file {}".format(i))
            self.sfile[i].close()
        for c in self.cons:
            print(" -/-> tcp {}".format(c[1]))
            c[0].close()
        self.sock.close()

if __name__ == '__main__':
    ms = None
    try:
        print("initializing server")
        ms = MathServer()
        ms.start() #blocking
    except KeyboardInterrupt:
        print("\nforce closing server")
    try:
        print("closing sockets")
        ms.close()
    except Exception as e:
        print(e)
        print("failed to close sockets")

