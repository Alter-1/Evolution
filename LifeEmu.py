#!/usr/bin/python
#//import tkinter
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
from World import L

PrintTextBox = None
TextArea = None

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



def AddXtoVideoStream(videoStream):
    global gX, gY, gXRayImg
    if gX == None:
        return videoStream

    return videoStream    

def onclick(e):
    global gX, gY, gXRayImg, XRimage, ghImage
    gX=e.x
    gY=e.y
    print("Cooordinates %d %d"%(gX,gY))

    return(gX,gY)

def Save():
    try:
        fn = asksaveasfilename(initialdir="./", initialfile="Earth.lsworld", title="Ssave the World", filetypes=(("Life simulator world", "*.lsworld"),))
        World.Save(fn)
    except Exception as e:
        print('ERR: '+ str(e))
    return
         
def Load():
    try:
        fn = askopenfilename(initialdir="./", title="Select World", filetypes=(("Life simulator world", "*.lsworld"),))
        World.Load(fn)
    except Exception as e:
        print('ERR: '+ str(e))
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
    TextArea.grid(column = 0, row = 0, columnspan=4)

    mtTextArea = AsyncTextBox.AsyncTextBox(gui, PrintTextBoxReal)
    PrintTextBox = mtTextArea.PrintTextBox
#--------------------------------------------- Video Frame -------------------------------------------------------------

    video = VideoStreamWindow(gui, 300, 300)

    commonframe = LabelFrame(gui, text="Modes", width=600)
    
    #commonframe.pack(fill="both", expand="yes")
    commonframe.grid(column = 0, row = 3, columnspan=4)
    commonframe.configure(background='black',foreground='green')

    btAge   = ttk.Button(commonframe, text = "Age/energy", command = lambda: video.SetMode(L.age   )).grid(column = 1, row = 1,sticky=W, padx=8, pady=5)
    btEnergy= ttk.Button(commonframe, text = "Energy",     command = lambda: video.SetMode(L.energy)).grid(column = 2, row = 1,sticky=W, padx=8, pady=5)
    btExp   = ttk.Button(commonframe, text = "Exp",        command = lambda: video.SetMode(L.exp   )).grid(column = 3, row = 1,sticky=W, padx=8, pady=5)

    btSahre = ttk.Button(commonframe, text = "Share", command = lambda: video.SetMode(L.share     )).grid( column = 1, row = 2,sticky=W, padx=8, pady=5)
    btAgg   = ttk.Button(commonframe, text = "Aggr",  command = lambda: video.SetMode(L.aggressive)).grid( column = 2, row = 2,sticky=W, padx=8, pady=5)
    btIQ    = ttk.Button(commonframe, text = "IQ",    command = lambda: video.SetMode(L.iq        )).grid( column = 3, row = 2,sticky=W, padx=8, pady=5)
    btDef   = ttk.Button(commonframe, text = "Def",   command = lambda: video.SetMode(L.defence   )).grid( column = 4, row = 2,sticky=W, padx=8, pady=5)

    btMob   = ttk.Button(commonframe, text = "Mob",   command = lambda: video.SetMode(L.mobility  )).grid( column = 1, row = 3,sticky=W, padx=8, pady=5)
    btFert  = ttk.Button(commonframe, text = "Fert",  command = lambda: video.SetMode(L.fert      )).grid( column = 2, row = 3,sticky=W, padx=8, pady=5)

    btSave  = ttk.Button(commonframe, text = "Save",  command = Save).grid(column = 1, row = 4,sticky=W, padx=8, pady=5)
    btLoad  = ttk.Button(commonframe, text = "Load",  command = Load).grid(column = 2, row = 4,sticky=W, padx=8, pady=5)

     # start textbox and progress bar message queues
    mtTextArea.periodicCall()

    video.Start()

    gui.mainloop() 
    try:
        video.Stop()
    except:
        pass
        

 