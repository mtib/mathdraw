import os
import time
import subprocess
import tkinter

fe, ge, d1, d2, dialog = 0, 0, 0, 0, 0
_pdflatex = "pdflatex -synctex=1 -shell-escape -interaction=nonstopmode "


def plot(f, d, y=[0, 0], g=""):
    tex = """\\documentclass[paper=a4,12pt]{scrartcl}
\\usepackage{pgfplots}
\\usepgfplotslibrary{external}
\\tikzexternalize
\\usepackage{filecontents}
\\begin{document}
\\begin{tikzpicture}
\\begin{axis}[legend style={at={(1,1)},anchor=north east},domain={""" + formatdomain(d) + """}""" + ("" if y == [0, 0] else ",ymin=" + str(y[0]) + ",ymax=" + str(y[1])) + """]
\\addplot[blue,samples=200] {""" + str(f) + """}; \\addlegendentry{""" + str(f) + """}""" + (("\\addplot[red,samples=200] {" + str(g) + "}; \\addlegendentry{" + str(g) + "}") if g != "" else "") + """
\\draw ({rel axis cs:0,0}|-{axis cs:0,0}) -- ({rel axis cs:1,0}|-{axis cs:0,0});
\\draw ({rel axis cs:0,0}-|{axis cs:0,0}) -- ({rel axis cs:0,1}-|{axis cs:0,0});
\\end{axis}
\\end{tikzpicture}
\\end{document}"""
    try:
        os.rmdir("plotting")
    except:
        pass
    try:
        os.mkdir("plotting")
    except:
        try:
            os.rename("plotting/plot-figure0.pdf", "plotting/old.pdf")
        except:
            pass
        try:
            os.remove("plotting/plot.png")
        except:
            pass
    tf = open("./plotting/plot.tex", "w")
    tf.write(tex)
    tf.close()
    os.chdir("plotting")
    subprocess.call(_pdflatex + str("plot.tex"), shell=True)
    subprocess.call(
        "convert -density 300 plot-figure0.pdf -quality 90 plot.png", shell=True)
    time.sleep(1)
    subprocess.call("convert plot.png -resize 400x260! plot_r.png", shell=True)
    time.sleep(1)
    os.chdir("..")
    return "plotting/plot_r.png"


def formatdomain(d):
    return str(d)[1:-1].replace(",", ":")


def main():
    print("pgf.py")
    demow()


def demo():
    f = str(input("f(x)="))
    d = [float(input("minx=")), float(input("maxx="))]
    return plot(f, d)


def demow():
    global dialog
    global fe
    global ge
    global d1
    global d2
    dialog = tkinter.Tk()
    dialog.title("Plotter")
    top = tkinter.Frame(dialog)
    bot = tkinter.Frame(dialog)
    tkinter.Label(top, text="f(x)=").grid(row=0)
    tkinter.Label(top, text="g(x)=").grid(row=1)
    tkinter.Label(top, text="minx=").grid(row=2)
    tkinter.Label(top, text="maxx=").grid(row=3)
    fe = tkinter.Entry(top)
    ge = tkinter.Entry(top)
    d1 = tkinter.Entry(top)
    d2 = tkinter.Entry(top)
    fe.grid(row=0, column=1)
    ge.grid(row=1, column=1)
    d1.grid(row=2, column=1)
    d2.grid(row=3, column=1)
    ok = tkinter.Button(bot, text="Plot", command=start)
    ok.pack(fill="x", expand=1)
    dialog.bind("<Return>", start)
    top.pack()
    bot.pack()
    tkinter.Toplevel.wait_window(dialog)


def start(event=""):
    global dialog
    global fe
    global ge
    global d1
    global d2
    gf = ge.get()
    f = fe.get()
    d = [float(d1.get()), float(d2.get())]
    fe = 0
    d1 = 0
    d2 = 0
    ge = 0
    dialog.destroy()
    dialog = 0
    plot(f, d, g=gf)


def ydemo():
    f = str(input("f(x)="))
    d = [float(input("minx=")), float(input("maxx="))]
    y = [float(input("miny=")), float(input("maxy="))]
    return plot(f, d, y)

if __name__ == "__main__":
    main()
