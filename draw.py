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
# return     =finish text input
# double lmb =cycle colors

import pgf
import time
import threading
import os, subprocess, sys # Using ps2pdf
import time # Filename
import socket
from threading import Thread

r = "#BB0000"
g = "#009900"
b = "#0000BB"
num = 0
color = [r, g, b]
arg0 = os.path.dirname(sys.argv[0])
filedir = arg0+"/" if len(arg0)>0 else ""

listenedText = ""
listenToText = False
textpos = [0, 0]
useLast = False
last = [0, 0]
pos = [0, 0]

sock = None
sfile = None
server = '127.0.0.1'
try:
    server = os.environ["MATHDRAW"]
    print("Using server:", server)
except:
    print("$MATHDRAW not defined, reverting to localhost")

basetitle = "MathDraw 5 - {}".format(server)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for i in range(101):
    try:
        sock.connect((server, 8228+i))
        break
    except:
        continue
sfile = sock.makefile()

accmsg = sfile.readline()
if accmsg != 'accept\n':
    print("didn't receive an accept message")
    sys.exit(1)

def main():
    import tkinter
    global root
    global canv
    root = tkinter.Tk()
    root.title(basetitle)
    canv = tkinter.Canvas(root, width=1280, height=720, background="#fff")
    canv.pack()
    canv.bind("<Button-1>", paint)
    canv.bind("<B1-Motion>", paint)
    canv.bind("c", cycle)
    canv.bind("<Button-2>", cycle)
    canv.bind("<ButtonRelease-1>", release)
    canv.bind("<Leave>", release)
    canv.bind("<B3-Motion>", erase)
    root.bind("<Left>", mleft)
    root.bind("<Right>", mright)
    root.bind("<Up>", mup)
    root.bind("<Down>", mdown)
    root.bind("t", write)
    root.bind("T", cmdInput)
    root.bind("<Return>", enter)
    root.bind("<Key>", listenT)
    root.bind("<BackSpace>", removeT)
    root.bind("D", plotting)
    root.bind("C", exportPdf)
    move()
    tkinter.mainloop()

def paint(event):
    global useLast
    x = int(canv.canvasx(event.x))
    y = int(canv.canvasy(event.y))
    if useLast:
        _paint(last[0], last[1], x, y, num % 3)
        sock.send('d:{:}:{:}:{:}:{:}:{}\n'.format(last[0], last[1], x, y, num % 3).encode('ascii'))
    else:
        pass
        #canv.create_oval(event.x-1,event.y-1,event.x+1,event.y+1, fill=color[num%3])
    last[0] = x
    last[1] = y
    useLast = True

def _paint(x1, y1, x2, y2, n):
    canv.create_line(x1, y1, x2, y2, fill=color[n], width=3)



def cycle(event):
    global num
    num = num + 1
    root.title(basetitle + " " + color[num%3])


def release(event):
    global useLast
    useLast = False


def mleft(event):
    canv.xview_scroll(-1280, "unit")
    pos[0] -= 1280
    move()


def mright(event):
    canv.xview_scroll(1280, "unit")
    pos[0] += 1280
    move()


def mup(event):
    canv.yview_scroll(-720, "unit")
    pos[1] -= 720
    move()


def mdown(event):
    canv.yview_scroll(720, "unit")
    pos[1] += 720
    move()


def move():
    sp = pos[:]
    sp[0] = int(sp[0] / 1280)
    sp[1] = int(sp[1] / 720)
    print("move(", sp, ")")
    space = 4
    canv.create_text(canv.canvasx(space), canv.canvasy(
        space), text=str(sp), anchor="nw", fill="#fff")
    canv.create_text(canv.canvasx(space), canv.canvasy(
        space), text=str(sp), anchor="nw", fill="#333")
    canv.create_line(canv.canvasx(400), canv.canvasy(
        720), canv.canvasx(400), canv.canvasy(720 - 260), fill="#ddd")
    canv.create_line(canv.canvasx(0), canv.canvasy(720 - 260),
                     canv.canvasx(400), canv.canvasy(720 - 260), fill="#ddd")


def erase(event):
    x = int(canv.canvasx(event.x))
    y = int(canv.canvasy(event.y))
    sock.send('e:{}:{}\n'.format(x,y).encode('ascii'))
    _erase(x, y)

def _erase(x, y):
    s = 20
    canv.create_oval(x - s, y - s, x + s, y + s, fill="white", outline="white")

def write(event):
    global listenToText
    global listenedText
    global textpos
    if listenToText:
        listenT(event)
        return
    listenToText = True
    textpos[0] = event.x
    textpos[1] = event.y
    print("Listening to Text")


def enter(event):
    global listenToText
    if listenToText:
        listenToText = False
        writeOut()


def writeOut():
    global listenedText
    x = int(canv.canvasx(textpos[0]))
    y = int(canv.canvasy(textpos[1]))
    _writeOut(x, y, listenedText)
    sock.send('t:{}:{}:{}\n'.format(x, y, listenedText).encode('ascii'))
    listenedText = ""
    print("\nText written")

def _writeOut(x, y, t):
    canv.create_text(x, y, text=t, font="Consolas 18 bold")


def listenT(event):
    global listenedText
    listenedText += event.char
    if listenToText:
        print("\033[1024D", end="")
        print(listenedText, end="")
        sys.stdout.flush()
    else:
        listenedText = ""


def removeT(event):
    global listenedText
    listenedText = listenedText[:-1]
    print("\033[1D \033[1D", end="")
    sys.stdout.flush()


def cmdInput(event):
    global listenToText
    global listenedText
    if listenToText:
        listenT(event)
        return
    t = str(input("Text:"))
    x = int(canv.canvasx(event.x))
    y = int(canv.canvasy(event.y))
    sock.send('t:{}:{}:{}\n'.format(x, y, t).encode('ascii'))
    _writeOut(x, y, t)
tr = False

def exportPdf(event):
    canv.postscript(file=filedir+"tmp.ps",colormode="color")
    try:
        os.mkdir(filedir+"images")
    except FileExistsError:
        pass
    os.system("convert \""+filedir+"tmp.ps\" \""+filedir+"images/{:x}.jpg\"".format(int(time.time())))
    os.system("rm \""+filedir+"tmp.ps\"")

def plotting(event):
    global listenToText
    global listenedText
    global tr
    if listenToText:
        listenedText += "D"
        print(listenedText)
        return
    mp = threading.Thread(target=multiPlot)
    mp.start()


def multiPlot():
    pgf.demow()
    print("finished generating")
    time.sleep(.5)
    print("printing image")
    global canv
    global p
    p = tkinter.PhotoImage(file="./plotting/plot_r.png")
    canv.create_image(canv.canvasx(0), canv.canvasy(720), anchor="sw", image=p)
    print("printed image")

def sock_receive():
    try:
        while True:
            msg = sfile.readline()[:-1]
            print(msg)
            mspl = msg.split(":")
            if msg[0] == 'e':
                #e:x:y
                _erase(int(mspl[1]), int(mspl[2]))
            elif msg[0] == 'd':
                #d:x1:y1:x2:y2:num
                _paint(int(mspl[1]), int(mspl[2]), int(mspl[3]), int(mspl[4]), int(mspl[5]))
            elif msg[0] == 't':
                #t:x:y:text
                _writeOut(int(mspl[1]), int(mspl[2]), mspl[3])
    except:
        return

if __name__ == '__main__':
    Thread(target=sock_receive).start()
    try:
        main()
    except KeyboardInterrupt:
        pass
    except:
        pass
    sock.send(b'close\n')
    sfile.close()
    sock.close()
