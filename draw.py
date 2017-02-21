#!/usr/bin/python3

"""MathDraw - a virtual whiteboard

with batteries included.
"""
# Controls:
# lmb        =paint
# rmb        =erase
# mmb        =cycle colors
# arrow keys =move canvas
# t          =text input
# T          =cli input
# return     =finish text input
# double lmb =cycle colors

import time
import threading
import os, subprocess, sys # Using ps2pdf
import time # Filename
import socket
import tkinter
from threading import Thread
from server import PORT, MAX_OFFSET

class MathClient():

    red = "#BB0000"
    green = "#009900"
    blue = "#0000BB"
    num = 0
    color = [red, green, blue]

    def __init__(self):
        self.host = socket.gethostname()
        self.server = None

        self.textaccum = ""
        self.listen = False
        self.textpos = [0, 0]
        self.last = [0, 0]
        self.pos = [0, 0]
        self.useLast = False
        self.follow = False

        self._connect()
        self._tkinter()


    def _connect(self):
        try:
            # look for env $MATHDRAW
            self.host = os.environ["MATHDRAW"]
        except:
            # TODO starting server when one is already up
            # locally on port n-1
            from server import MathServer
            # if not told to connect to remote
            # start local server
            self.server = MathServer()
            Thread(target=self.server.start, daemon=True).start()

        self.title = "MathDraw 5 - {}".format(self.host)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(MAX_OFFSET+1):
            try:
                self.sock.connect((self.host, PORT+i))
                break
            except:
                continue
        self.sfile = self.sock.makefile()

        answ = self.sfile.readline()
        if answ != 'accept\n':
            print("didn't receive an accept message")
            print("received:\n{}\n... instead".format(answ))

    def _tkinter(self):
        self.tk = tkinter.Tk(className="mathdraw")
        self.tk.title(self.title)
        self.tk.bind("<Left>",      self.mleft)
        self.tk.bind("<Right>",     self.mright)
        self.tk.bind("<Up>",        self.mup)
        self.tk.bind("<Down>",      self.mdown)
        self.tk.bind("t",           self.write)
        self.tk.bind("f",           self.followToggle)
        self.tk.bind("T",           self.cmdInput)
        self.tk.bind("<Return>",    self.enter)
        self.tk.bind("<Key>",       self.listenT)
        self.tk.bind("<BackSpace>", self.removeT)
        # self.tk.bind("D", self.plotting)

        self.canv = tkinter.Canvas(self.tk, width=1280, height=720, background="#fff")
        self.canv.pack()
        self.canv.bind("<Button-1>",        self.paint)
        self.canv.bind("<B1-Motion>",       self.paint)
        self.canv.bind("c",                 self.cycle)
        self.canv.bind("<Button-2>",        self.cycle)
        self.canv.bind("<ButtonRelease-1>", self.release)
        self.canv.bind("<Leave>",           self.release)
        self.canv.bind("<B3-Motion>",       self.erase)
        self._update()

    def start(self):
        tkinter.mainloop()

    def _cx(self, x):
        return int(self.canv.canvasx(x))

    def _cy(self, y):
        return int(self.canv.canvasy(y))

    def followToggle(self, event):
        self.follow = not self.follow
        self._update()

    def paint(self, event):
        x = self._cx(event.x)
        y = self._cy(event.y)
        lx = self.last[0]
        ly = self.last[1]
        if self.useLast:
            self._paint(lx, ly, x, y, self.num % 3)
            self.sock.send('d:{}:{}:{}:{}:{}\n'.format(lx, ly, x, y, self.num % 3).encode('ascii'))
        else:
            self.useLast = True
        self.last[0] = x
        self.last[1] = y

    def _paint(self, x1, y1, x2, y2, n):
        c = self.color[n]
        self.canv.create_line(x1, y1, x2, y2, fill=c, width=3)
        self.canv.create_oval(x1-1,y1-1,x1+1,y1+1, fill=c, width=0)

    def cycle(self, event):
        self.num = (self.num + 1) % len(self.color)
        root.title(self.title + " " + self.color[self.num])


    def release(self, event):
        self.useLast = False


    def mleft(self, event):
        self._scroll('left')


    def mright(self, event):
        self._scroll('right')


    def mup(self, event):
        self._scroll('up')


    def mdown(self, event):
        self._scroll('down')

    def _scroll(self, direction):
        dist = 2
        dx = 0
        dy = 0
        if direction == 0 or direction == 'up':
            self.canv.yview_scroll(-dist, "pages")
            dy = -720
        elif direction == 1 or direction == 'right':
            self.canv.xview_scroll( dist, "pages")
            dx = 1280
        elif direction == 2 or direction == 'down':
            self.canv.yview_scroll( dist, "pages")
            dy = 720
        elif direction == 3 or direction == 'left':
            self.canv.xview_scroll(-dist, "pages")
            dx = -1280
        self.pos[0] += dx
        self.pos[1] -= dy
        self._update()


    def _change(self, wx, wy, s):
        pos = "[{}, {}]".format(wx, wy)
        self._blockErase(0, 0, 6 * len(pos) + 8, 20)
        self.canv.create_text(self._cx(s), self._cy(s), text=pos, anchor="nw", fill="#000")

    def _blockErase(self, x, y, width, height):
        self.canv.create_rectangle(self._cx(x), self._cy(y), self._cx(x+width), self._cy(y+height), fill="#FFF", width=0)

    def _update(self):
        space = 4
        self._change(int(self.pos[0]/1280), int(self.pos[1]/720), space)
        self._blockErase(0, 20, 40, 20)
        if self.follow:
            self.canv.create_text(self._cx(space), self._cy(space+20), text="follow", anchor="nw", fill="#000")

    def erase(self, event):
        x = self._cx(event.x)
        y = self._cy(event.y)
        self.sock.send('e:{}:{}\n'.format(x,y).encode('ascii'))
        self._erase(x, y)

    def _erase(self, x, y):
        s = 20
        self.canv.create_oval(x - s, y - s, x + s, y + s, fill="white", outline="white")

    def write(self, event):
        if self.listen:
            self.listenT(event)
            return
        print("Listening to Text")
        self.listen = True
        self.textpos[0] = event.x
        self.textpos[1] = event.y


    def enter(self, event):
        if self.listen:
            self.listen = False
            self.writeOut()


    def writeOut(self):
        x = self._cx(textpos[0])
        y = self._cy(textpos[1])
        _writeOut(x, y, self.textaccum)
        self.sock.send('t:{}:{}:{}\n'.format(x, y, self.textaccum).encode('ascii'))
        self.textaccum = ""
        print("\nText written")

    def _writeOut(self, x, y, t):
        self.canv.create_text(x, y, text=t, font="\"Times New Roman\" 18 regular")


    def listenT(self, event):
        if self.listen:
            self.textaccum += event.char
            print("\033[1024D",   end="")
            print(self.textaccum, end="")
            sys.stdout.flush()
        else:
            self.textaccum = ""


    def removeT(self, event):
        self.textaccum = self.textaccum[:-1]
        print("\033[1D \033[1D", end="")
        sys.stdout.flush()


    def cmdInput(event):
        if self.listen:
            self.listenT(event)
            return
        t = str(input("Text:"))
        x = self._cx(event.x)
        y = self._cy(event.y)
        self.sock.send('t:{}:{}:{}\n'.format(x, y, t).encode('ascii'))
        self._writeOut(x, y, t)

    def plotting(self, event):
        print("plotting not implemented")

    def server_communication(self):
        Thread(target=self._sock_receive).start()

    def _sock_receive(self):
        try:
            while True:
                msg = self.sfile.readline()[:-1]
                mspl = msg.split(":")
                if msg[0] == 'e':
                    #e:x:y
                    self._erase(int(mspl[1]), int(mspl[2]))
                elif msg[0] == 'd':
                    #d:x1:y1:x2:y2:num
                    self._paint(int(mspl[1]), int(mspl[2]), int(mspl[3]), int(mspl[4]), int(mspl[5]))
                elif msg[0] == 't':
                    #t:x:y:text
                    self._writeOut(int(mspl[1]), int(mspl[2]), mspl[3])
                elif msg[0] == 'c':
                    print("change to [{}, {}] received".format(mspl[1], mspl[2]))
                else:
                    print("unknown server response")
        except:
            print("return client receive")
            return

# TODO implement MathClient._servercom(...)
# that checks for BrokenPipeError and tries to reconnect

def main():
    client = MathClient()
    try:
        client.server_communication()
        client.start()
    except KeyboardInterrupt:
        pass
    except:
        pass
    client.sock.send(b'close\n')
    time.sleep(0.5)

if __name__ == '__main__':
    main()
