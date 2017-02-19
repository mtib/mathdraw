#!/usr/bin/env python3

"""Server side of MathDraw application

should be hosted on $MATHDRAW so the client connects properly
"""

import socket
import os
import time
from threading import Thread

class MathServer():
    sfile = dict()
    sock = None
    cons = []

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.bind((socket.gethostname(), 8228))
                break
            except Exception as e:
                print("waiting for port 8228 to free (wait 5s)")
                time.sleep(5)
        self.sock.listen(3)


    def _accept(self, conn, addr):
        print(" <- started thread for {}".format(addr))
        self.sfile[addr] = conn.makefile()
        self.cons.append((conn, addr))
        conn.send(b'accept\n')
        print(" <- accepted connection for {}".format(addr))
        while True:
            msg = 'close'
            try:
                msg = self.sfile[addr].readline()
            except ConnectionResetError:
                msg = 'close'
            if len(msg) == 0:
                print("newline received")
                continue
            if msg == 'close':
                conn.close()
                self.sfile[addr].close()
                self.cons.remove((conn,addr))
                self.sfile.pop(addr)
                print(" -/-> tcp & file {}".format(addr))
                return
            elif msg[0] == 'd':
                print("draw command")
            elif msg[0] == 'e':
                print("erase command")
            else:
                print("unknown command by {}".format(addr))

    def start(self):
        print("starting server")
        while True:
            c, a = self.sock.accept()
            print(" -> connection: {}".format(a))
            Thread(target=self._accept, args=[c, a]).start()

    def close(self):
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

