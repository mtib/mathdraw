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

import os, subprocess, sys # Using ps2pdf
import socket
import string
import threading
import time
import time # Filename
import tkinter
from server import PORT, MAX_OFFSET
from threading import Thread

WIDTH = 1280
HEIGHT = 720

class MathClient():

    black = "#050505"
    red = "#BB0000"
    green = "#009900"
    blue = "#0000BB"
    num = 0
    color = [black, red, green, blue]
    colorName = ["black", "red", "green", "blue"]

    def __init__(self):
        self.host = socket.gethostname()
        self.server = None

        self.textaccum = ""
        self.listen = False
        self.textpos = (0, 0)
        self.last = (0, 0)
        self.delta = (0, 0)
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
        self.tk.bind("<Left>",      lambda e: self._scroll('left'))
        self.tk.bind("<Right>",     lambda e: self._scroll('right'))
        self.tk.bind("<Up>",        lambda e: self._scroll('up'))
        self.tk.bind("<Down>",      lambda e: self._scroll('down'))
        self.tk.bind("t",           self.write)
        self.tk.bind("f",           self.followToggle)
        self.tk.bind("T",           self.cmdInput)
        self.tk.bind("<Return>",    self.enter)
        self.tk.bind("<Key>",       self.listenT)
        self.tk.bind("<BackSpace>", self.removeT)
        # self.tk.bind("D", self.plotting)

        self.canv = tkinter.Canvas(self.tk, width=WIDTH, height=HEIGHT, background="#fff")
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

    def _cx(self, x, f=int):
        return f(self.canv.canvasx(x))

    def _cy(self, y, f=int):
        return f(self.canv.canvasy(y))

    def _c(self, event, f=int):
        return (f(self._cx(event.x, f)), f(self._cy(event.y, f)))

    def followToggle(self, event):
        if self.listen:
            self.listenT(event)
            return
        self.follow = not self.follow
        self._update()

    def paint(self, event):
        (x, y) = self._c(event, float)
        (lx, ly) = self.last
        if self.useLast:
            x = (x + lx+self.delta[0]) / 2.0
            y = (y + ly+self.delta[1]) / 2.0
            self._paint(lx, ly, x, y, self.num % len(self.color))
            self.sock.send('d:{:.0f}:{:.0f}:{:.0f}:{:.0f}:{}\n'.format(lx, ly, x, y, self.num % len(self.color)).encode('ascii'))
            self.delta = (x-lx, y-ly)
        else:
            self.useLast = True
            self.delta = (0, 0)
        self.last = (x, y)

    def _paint(self, x1, y1, x2, y2, n):
        c = self.color[n]
        self.canv.create_line(x1, y1, x2, y2, fill=c, width=2)
        self.canv.create_oval(x1-1,y1-1,x1+1,y1+1, fill=c, width=0)

    def cycle(self, event):
        self.num = (self.num + 1) % len(self.color)
        self.tk.title(self.title + " " + self.color[self.num])
        self._update()

    def release(self, event):
        self.useLast = False

    def _scroll(self, direction):
        dist = 2
        dx = 0
        dy = 0
        if direction == 0 or direction == 'up':
            self.canv.yview_scroll(-dist, "pages")
            dy = -HEIGHT
        elif direction == 1 or direction == 'right':
            self.canv.xview_scroll( dist, "pages")
            dx = WIDTH
        elif direction == 2 or direction == 'down':
            self.canv.yview_scroll( dist, "pages")
            dy = HEIGHT
        elif direction == 3 or direction == 'left':
            self.canv.xview_scroll(-dist, "pages")
            dx = -WIDTH
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
        self._change(int(self.pos[0]/WIDTH), int(self.pos[1]/HEIGHT), space)
        self._blockErase(0, 20, 40, 20)
        self.canv.create_text(self._cx(space), self._cy(space+20), text=self.colorName[self.num], anchor="nw", fill=self.color[self.num])
        self._blockErase(0, 40, 40, 20)
        if self.follow:
            self.canv.create_text(self._cx(space), self._cy(space+40), text="follow", anchor="nw", fill="#000")

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
        print("Listening to Text\n -> ", end="")
        sys.stdout.flush()
        self.listen = True
        self.textpos = (event.x, event.y)

    def enter(self, event):
        if self.listen:
            self.listen = False
            self.writeOut()

    def writeOut(self):
        x = self._cx(self.textpos[0])
        y = self._cy(self.textpos[1])
        self._writeOut(x, y, self.textaccum)
        self.sock.send('t:{}:{}:{}\n'.format(x, y, self.textaccum).encode('ascii'))
        self.textaccum = ""
        print("\nText written")

    def _writeOut(self, x, y, t):
        self.canv.create_text(x, y, text=t, font="\"Times New Roman\" 18")

    def listenT(self, event):
        if self.listen and event.char in string.printable:
            self.textaccum += event.char
            print("\033[1024D -> \033[34;4m", end="")
            print(self.textaccum, end="\033[0m")
            sys.stdout.flush()
        else:
            self.textaccum = ""

    def removeT(self, event):
        self.textaccum = self.textaccum[:-1]
        print("\033[1D \033[1D", end="")
        sys.stdout.flush()

    def cmdInput(self, event):
        if self.listen:
            self.listenT(event)
            return
        t = str(input("Text:"))
        x = self._cx(event.x)
        y = self._cy(event.y)
        self.sock.send('t:{}:{}:{}\n'.format(x, y, t).encode('ascii'))
        self._writeOut(x, y, t)

    def plotting(self, event):
        print("\033[31;1mplotting not implemented\033[0m")

    def server_communication(self):
        Thread(target=self._sock_receive).start()

    def _sock_receive(self):
        try:
            while True:
                msg = self.sfile.readline()[:-1]
                if len(msg) == 0:
                    raise Exception(" <- server down")
                mstr = msg.split(":")[1:]
                mdat = []
                if msg[0] == 't':
                    mdat = list(map(int, mstr[:-1]))
                else:
                    mdat = list(map(int, mstr))

                if msg[0] == 'e':
                    #e:x:y
                    self._erase(mdat[0], mdat[1])
                elif msg[0] == 'd':
                    #d:x1:y1:x2:y2:num
                    self._paint(mdat[0], mdat[1], mdat[2], mdat[3], mdat[4])
                elif msg[0] == 't':
                    #t:x:y:text
                    self._writeOut(mdat[0], mdat[1], mstr[2])
                elif msg[0] == 'c':
                    print(" <- change to [{}, {}] received".format(mdat[0], mdat[1]))
                else:
                    print("unknown server response")
        except Exception as e:
            print(e)
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
