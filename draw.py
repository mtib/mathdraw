#!/usr/bin/python3
import tkinter
import pgf
import time
import threading
import os, subprocess, sys # Using ps2pdf
import time # Filename

# Controls:
#lmb        =paint
#rmb        =erase
# mmb        =cycle colors
# arrow keys =move canvas
# t          =text input
# return     =finish text input
# double lmb =cycle colors

root = tkinter.Tk()
canv = tkinter.Canvas(root, width=1280, height=720, background="#fff")
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

basetitle = "MathDrawPy 5"


def paint(event):
    global useLast
    x = canv.canvasx(event.x)
    y = canv.canvasy(event.y)
    if useLast:
        canv.create_line(last[0], last[1], x, y, fill=color[num % 3], width=3)
    else:
        pass
        #canv.create_oval(event.x-1,event.y-1,event.x+1,event.y+1, fill=color[num%3])
    last[0] = x
    last[1] = y
    useLast = True


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
    print(sp)
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
    s = 20
    x = canv.canvasx(event.x)
    y = canv.canvasy(event.y)
    canv.create_oval(x - s, y - s, x + s, y + s, fill="white", outline="white")


def write(event):
    global listenToText
    global listenedText
    global textpos
    if listenToText:
        listenedText += "t"
        print(listenedText)
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
    canv.create_text(canv.canvasx(textpos[0]), canv.canvasy(
        textpos[1]), text=listenedText, font="Consolas 18 bold")
    listenedText = ""
    print("Text written")


def listenT(event):
    global listenedText
    listenedText += event.char
    print(listenedText)


def removeT(event):
    global listenedText
    listenedText = listenedText[:-1]
    print(listenedText)


def cmdInput(event):
    global listenToText
    global listenedText
    if listenToText:
        listenedText += "T"
        print(listenedText)
        return
    t = str(input("Text:"))
    canv.create_text(canv.canvasx(event.x), canv.canvasy(
        event.y), text=t, font="Consolas 18 bold")
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


root.title(basetitle)
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
