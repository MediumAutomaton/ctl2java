# Dead-simple TkInter GUI to set up arguments to CTL2Java
# File last updated 9-7-25

import os
import traceback
from tkinter import Tk, filedialog, Checkbutton, Button, BooleanVar, Entry, Label

root = Tk()
root.title("CTL2Java Launcher GUI")
root.maxsize(800, 600)

infile1 = "Gamepad1 Mapping File"
infile2 = "Gamepad2 Mapping File"

def getinfile1():
    global infile1
    infile1 = filedialog.askopenfilename(initialdir=os.getcwd(), title="Gamepad1 Mapping File")
    if1button.config(text=infile1)

def getinfile2():
    global infile2
    infile2 = filedialog.askopenfilename(initialdir=os.getcwd(), title="Gamepad2 Mapping File")
    if2button.config(text=infile2)

if1button = Button(root, text=infile1, command=getinfile1)
if1button.pack()

if2button = Button(root, text=infile2, command=getinfile2)
if2button.pack()

Label(root, text="Output File Name").pack()
outfilebox = Entry(root)
outfilebox.pack()

Label(root, text="Output Package Name").pack()
outpackagebox = Entry(root)
outpackagebox.pack()

verify = BooleanVar()
verifybox = Checkbutton(root, text="Only verify files", variable=verify)
verifybox.pack()

debug = BooleanVar()
debugbox = Checkbutton(root, text="Extra long debug output", variable=debug)
debugbox.pack()

indy = BooleanVar()
indy.set(True)
fieldy = BooleanVar()

def noIndy():
    indy.set(False)

def noFieldy():
    fieldy.set(False)

indybox = Checkbutton(root, text="Indy drive type", variable=indy, command=noFieldy)
indybox.pack()
fieldybox = Checkbutton(root, text="Fieldy drive type", variable=fieldy, command=noIndy)
fieldybox.pack()

def run():
    if infile1 == "Gamepad1 Mapping File":
        Label(root, text="Must specify Gamepad1 Mapping File").pack()
    else:
        Label(root, text="Building command").pack()
        command = "python3 ctl2java.py --infile1="
        command += infile1
        if infile2 != "Gamepad2 Mapping File":
            command += " --infile2="
            command += infile2
        command += " --outfile="
        command += outfilebox.get()
        command += " --outpackage="
        command += outpackagebox.get()
        if debug.get():
            command += " --debug"
        if verify.get():
            command += " --verify"
        if indy.get():
            command += " --drivetype=indy"
        elif fieldy.get():
            command += " --drivetype=fieldy"
        Label(root, text="Running: " + command).pack()
        try:
            os.system(command)
            Label(root, text="Done (maybe) - check console to see what exactly happened").pack()
        except:
            Label(root, text=traceback.format_exc()).pack()

runbutton = Button(root, text="Convert", command=run)
runbutton.pack()

root.mainloop()
