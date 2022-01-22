#!/usr/bin/python
import tkinter as tk
from tkinter import *
from tkinter import ttk
#from tkinter as tk
from ttkthemes import ThemedTk
import sys
import os
from os import path
import multiprocessing
from RtspFrame import *

import AsyncTextBox
from PIL import ImageTk, Image
import cv2
import numpy as np

import threading
import socket
# import messagebox class from tkinter 
from tkinter import messagebox 
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from os import path
from time import sleep
import subprocess
import re
from shutil import *
from functools import reduce
import World
from WorldConst import L, T
from WorldOptions import *

PrintTextBox = None
TextArea = None
lbEpoch = None

lbVis = None
vMode = 0

chkZIQ_var  = None
chkLres_var = None

w = 300
h = 300
N = 2500

def printX(myStr):
    print(myStr)


def PrintTextBoxReal(myStr):
    #TextArea.insert(END, '\r\n' + myStr)
    #printX("UILOG: "+myStr)
    global TextArea
    printX(myStr)
    if(TextArea == None):
        return
    #if(bStop):
    #    return
    TextArea.insert(END, myStr)
    TextArea.see(END)
#end PrintTextBoxReal()


def ClearScreen():
    TextArea.delete("1.0", "end")

def SetMode(mode):
    global video, vMode
    video.SetMode(mode)
    vMode = mode
#end SetMode()

def SetOptions():
    global gui
    o = World.PackWorld()
    r = WorldOptions.Show(gui, o)
    if(r):
        World.UnpackWorld(o)
#end SetOptions()

def UpdateOnFrameChange():
    global lbEpoch, lbVis, vMode

    lbEpoch.config(text=str(World.gEpoch))
    lbEpoch.update()
    #printX("Epoch:"+str(World.gEpoch))
    lbVis.config(text=World.LayerName[vMode])
    lbVis.update()
#end UpdateOnFrameChange()

def onclick(e):
    global gX, gY, gXRayImg, XRimage, ghImage
    gX=e.x
    gY=e.y
    print("Cooordinates %d %d"%(gX,gY))

    return(gX,gY)
#end onclick()

gOpenSaveDir = "."
gOpenSaveName = "Earth.lsworld"

def Save():
    global gOpenSaveDir, gOpenSaveName
    try:
        fn = asksaveasfilename(initialdir=gOpenSaveDir+"/", initialfile=gOpenSaveName, title="Save the World", filetypes=(("Life simulator world", "*.lsworld"),))
        if(not fn):
            return
        gOpenSaveDir = path.dirname(fn)
        gOpenSaveName = path.basename(fn)
        World.Save(fn)
    except Exception as e:
        print('ERR: '+ str(e))
    return
#end Save()
         
def Load():
    global gOpenSaveDir, gOpenSaveName
    try:
        fn = askopenfilename(initialdir=gOpenSaveDir+"/", title="Select World", filetypes=(("Life simulator world", "*.lsworld"),))
        if(not fn):
            return
        gOpenSaveDir = path.dirname(fn)
        gOpenSaveName = path.basename(fn)
        World.Load(fn)

        chkZIQ_var.set( World.gIQ0          )
        chkLres_var.set(World.gAllowLocalRes)
        print("IQ0="+str(World.gIQ0)+" LocalRes="+str(World.gAllowLocalRes))

    except Exception as e:
        print('ERR: '+ str(e))
    return
#end Load()

def New():
    #global gW, gH
    global w, h, N
    bLocked = False
    try:
        print('Lock')
        World.WLockWait()
        bLocked = True
        print('Stop')
        World.Stop()
        print('Init')

        World.gIQ0           = (chkZIQ_var.get() == 1)
        World.gAllowLocalRes = (chkLres_var.get() == 1)

        #World.CreateMatrix(World.gW, World.gH, 2500)
        World.CreateMatrix(w, h, N)
    except Exception as e:
        print('ERR: '+ str(e))

    if(bLocked):
        print('Release')
        World.WRelease()

    print('go!')
    return

if __name__ == "__main__" : 


    msg ="Life simulator\n"
	# create a GUI window   
    
    gui = ThemedTk(theme='black')
    style = ttk.Style()
    style.theme_use('black')
    style.configure('TButton', background = 'Black', foreground = 'Lime')
    gui.configure(background='black')
    print(gui.get_themes())
    gui.title("Life simulator")
    gui.geometry("660x850")
    TextArea = Text(gui, height = 5, width =80, font = "lucida 10", background='DimGray',foreground='Lime')
    #TextArea.pack()
    TextArea.grid(column = 0, row = 0, columnspan=1)

    mtTextArea = AsyncTextBox.AsyncTextBox(gui, PrintTextBoxReal)
    PrintTextBox = mtTextArea.PrintTextBox
#--------------------------------------------- Video Frame -------------------------------------------------------------

    video = VideoStreamWindow(gui, w, h)
    World.CreateMatrix(w, h, N)

#--------------------------------------------- Buttons  -------------------------------------------------------------

    commonframe = LabelFrame(gui, text="View", width=800)
    
    #commonframe.pack(fill="both", expand="yes")
    commonframe.grid(column = 0, row = 2, columnspan=1)
    commonframe.configure(background='black',foreground='green')

    btAge   = ttk.Button(commonframe, text = "Age/energy", command = lambda: SetMode(L.age   )).grid(column = 1, row = 1,sticky=W, padx=8, pady=5)
    btEnergy= ttk.Button(commonframe, text = "Energy",     command = lambda: SetMode(L.energy)).grid(column = 2, row = 1,sticky=W, padx=8, pady=5)
    btExp   = ttk.Button(commonframe, text = "Exp",        command = lambda: SetMode(L.exp   )).grid(column = 3, row = 1,sticky=W, padx=8, pady=5)
    btColor = ttk.Button(commonframe, text = "Color",      command = lambda: SetMode(L.color )).grid(column = 4, row = 1,sticky=W, padx=8, pady=5)
    btMyth  = ttk.Button(commonframe, text = "Myth",       command = lambda: SetMode(L.myth  )).grid(column = 5, row = 1,sticky=W, padx=8, pady=5)

    lbEpoch = ttk.Label(commonframe, text="-")
    lbEpoch.grid(column = 6, row = 1)

    lbVis = ttk.Label(commonframe, text="")
    lbVis.grid  (column = 7, row = 1)

    btSahre = ttk.Button(commonframe, text = "Share", command = lambda: SetMode(L.share     )).grid( column = 1, row = 2,sticky=W, padx=8, pady=5)
    btAgg   = ttk.Button(commonframe, text = "Aggr",  command = lambda: SetMode(L.aggressive)).grid( column = 2, row = 2,sticky=W, padx=8, pady=5)
    btIQ    = ttk.Button(commonframe, text = "IQ",    command = lambda: SetMode(L.iq        )).grid( column = 3, row = 2,sticky=W, padx=8, pady=5)
    btDef   = ttk.Button(commonframe, text = "Def",   command = lambda: SetMode(L.defence   )).grid( column = 4, row = 2,sticky=W, padx=8, pady=5)
    btMob   = ttk.Button(commonframe, text = "Mob",   command = lambda: SetMode(L.mobility  )).grid( column = 5, row = 2,sticky=W, padx=8, pady=5)
    btFert  = ttk.Button(commonframe, text = "Fert",  command = lambda: SetMode(L.fert      )).grid( column = 6, row = 2,sticky=W, padx=8, pady=5)

    chkZIQ_var  = tk.IntVar(commonframe, int(World.gIQ0          ))
    chkLres_var = tk.IntVar(commonframe, int(World.gAllowLocalRes))

    chkZIQ  = ttk.Checkbutton(commonframe, text = "0-IQ",      variable=chkZIQ_var ).grid(column = 1, row = 3,sticky=W, padx=8, pady=5)
    chkLres = ttk.Checkbutton(commonframe, text = "Local res", variable=chkLres_var).grid(column = 2, row = 3,sticky=W, padx=8, pady=5)

    btOpt   = ttk.Button(commonframe, text = "Options",command= SetOptions ).grid(column = 3, row = 3,sticky=W, padx=8, pady=5)
    btNew   = ttk.Button(commonframe, text = "New",   command = New        ).grid(column = 4, row = 3,sticky=W, padx=8, pady=5)

    btSave  = ttk.Button(commonframe, text = "Save",  command = Save       ).grid(column = 1, row = 4,sticky=W, padx=8, pady=5)
    btLoad  = ttk.Button(commonframe, text = "Load",  command = Load       ).grid(column = 2, row = 4,sticky=W, padx=8, pady=5)

     # start textbox and progress bar message queues
    mtTextArea.periodicCall()

    video.SetUpdateUI(UpdateOnFrameChange)
    video.Start()

    gui.mainloop() 
    print("end of gui.mainloop()")
    try:
        video.Stop()
    except:
        pass
        

 