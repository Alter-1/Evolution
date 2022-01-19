import tkinter as tk 

import World
from WorldConst import L, T

import math

from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedTk

import cv2  
from PIL import Image
from PIL import ImageTk
import threading
import os
import queue
import time
import numpy as np

errCnt = 0

class VideoStreamWindow():
    def __init__(self, window, w, h):
        self.window = window
        self.init_done = False
        self.w = w
        self.h = h
        self.res_queue = queue.Queue()
        self.daemon = VideoCaptureDaemon(self.res_queue, w, h)
        #self.daemon.start()
        self.interval = 10 # Interval in ms to get the latest frame
        self.stop = False
        # Create canvas for image
        self.canvas = tk.Canvas(self.window, width=w*2, height=h*2, bg='black')
        self.canvas.grid(row=1, column=0, columnspan=1)
        # Update image on canvas
        window.after(self.interval, self.update_image)
        #self.button = ttk.Button()
    #end __init__()
        
    def Crop(self, x, y):
        self.daemon.Crop(x, y)

    def VFlip(self, vflip):
        self.daemon.VFlip(vflip)

    def SetPostProcessing(self, f):
        self.daemon.PostProcessing = f

    def update_image(self):    
        # Get the latest frame and convert image format
        global errCnt
        try:
            #img = self.res_queue.get(block=True, timeout=timeout)
            img = self.res_queue.get(block=False)
            self.cur_image = img
            self.hImage = self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        except:
            #print('cv2.VideoCapture: could not grab input ({}). Timeout occurred after {:.2f}s'.format(video, timeout)) 
            if(errCnt % 1000) == 0:       
                print("Lost images: %d."%errCnt)
            errCnt += 1

        #end try/except
        # Repeat every 'interval' ms
        if(self.stop):
            return
        try:
            self.window.after(self.interval, self.update_image)
        except:
            Stop()
    #end update_image()

    def SetMode(self, mode):
        self.daemon.mode = mode

    def Start(self):
        self.daemon.start()

    def Stop(self):
        try:
            self.stop = True
            self.daemon.Stop()
            self.daemon.join()
            #while(self.daemon.active):
            #    time.sleep(0.1)
        except:
            pass
    #end Stop()

#end class VideoStreamWindow

def crop_center(img,cropx,cropy):
    y,x,c = img.shape
    startx = x//2 - cropx//2
    starty = y//2 - cropy//2    
    return img[starty:starty+cropy, startx:startx+cropx, :]
#end crop_center()

class VideoCaptureDaemon(threading.Thread):

    def __init__(self, result_queue, w, h):
        super().__init__()
        self.daemon = True

        self.init_done = False
        self.result_queue = result_queue
        self.stop = False
        self.PostProcessing = None
        self.active = False
        self.mode = 0
        self.prev_mode = -1
        self.prev_epoch = -1

        self.w = w
        self.h = h
        self.data = np.zeros((self.w*2, self.h*2, 3), dtype=np.uint8)
        #self.data[0:256, 0:256] = [255, 0, 0] # red patch in upper left
        World.CreateMatrix(w, h, 4500)

        self.daemon = SimThread()
        #self.daemon.start()
    #end __init__()

    def Stop(self):
        self.stop = True
        self.daemon.Stop()
    #end Stop()

    def NextFrame(self):
        #World.Next()

        if(self.prev_mode == self.mode and self.prev_epoch == World.gEpoch):
            return None

        self.prev_mode = self.mode    
        self.prev_epoch = World.gEpoch

        lMatrix = np.copy(World.gMatrix)

#        for x in range(self.w):
#            for y in range(self.h):

        x = 0
        #for ax in lMatrix:
        while(x<self.w):
            y = 0
            #for lItem in ax:
            while(y<self.h):

                g = 0
                r = 0
                b = 0

                #lItem = lMatrix[x,y]
                sex = lMatrix.item((x,y, L.sex))
                age = lMatrix.item((x,y, L.age))
                ctype = lMatrix.item((x,y, L.ctype))

                if(self.mode == L.color):
                    if(ctype == T.person):
                        color = lMatrix.item((x,y, L.color))
                        r = 63 + int(((color & 0xe0) / 256) * 192)
                        g = 63 + int(((color & 0x18) / 32 ) * 192)
                        b = 63 + int(((color & 0x07) / 8  ) * 192)
                
                elif(self.mode == 0 or self.mode == L.age):

                    #if(lItem[L.ctype] == T.ground):
                    if(ctype == T.ground):
                        #g = 50+int(lItem[L.resources]*1.5)
                        g = 50+int(lMatrix.item((x,y, L.resources))*1.2)  # 0-150
                    else:
                        #print("@"+str(x)+"x"+str(y))
                        
                        #if(lItem[L.sex] == T.male):
                        if(sex == T.male):
                            b = 250-age*2
                        else:
                            r = 250-age*2
                        
                        g = 50 + math.log(1+lMatrix.item((x,y, L.energy)))*36   # 0-250
                
                #if(self.mode > L.age):
                else:
                    if(ctype == T.person):

                        #v = lItem[self.mode]*2
                        v = lMatrix.item((x,y, self.mode))*2
                        
                        if(sex == T.male):
                            b = 50+v
                        else:
                            r = 50+v
                        
                        g = 50 + v


                rgb = [r, g, b]
                self.data[x*2:x*2+2,y*2:y*2+2] = rgb
                #self.data[x*2,y*2] = rgb
                #self.data[x*2+1,y*2] = rgb
                #self.data[x*2,y*2+1] = rgb
                #self.data[x*2+1,y*2+1] = rgb

                y+=1
            #end for y
            x+=1
        #end for x

        return self.data
    #end NextFrame()
    
    def run(self):
        self.daemon.start()
        self.active = True
        while(not self.stop):
            if(not self.init_done):
                if(not self.daemon.active):
                    print("Connecting...")
                    time.sleep(1)
                    continue
                self.init_done = True

            try:
                if(self.result_queue.empty()):
                    self.OGimage = self.NextFrame()
                    if(self.OGimage is None):
                        time.sleep(0.1)
                        continue
                    #imageAsArray = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB)
                                                         
                    # overlay with XRay image
                    if(not (self.PostProcessing == None)):
                        try:
                            resultImg = self.PostProcessing(self.OGimage)
                            self.OGimage = Image.fromarray(resultImg)
                        except Exception as e:
                            print('ERR: '+ str(e))
                            self.OGimage = Image.fromarray(self.OGimage) # to PIL format
                    else:
                        self.OGimage = Image.fromarray(self.OGimage) # to PIL format
                    
                    #self.image = self.OGimage.resize((300, 250), Image.ANTIALIAS)
                    
                    #self.image = Image.fromarray(self.OGimage)
                    self.image = ImageTk.PhotoImage(self.OGimage) # to ImageTk format
                    
                    self.result_queue.put(self.image)
                else:
                    #print("Skip frame")
                    pass
            except Exception as e:
                print('ERR: '+ str(e))
                print("Can't read frame, reconnect")
                self.cap = None
                #self.init_done = False
            #end try/expect

            #time.sleep(0.1)
        #end while()
        self.active = False
        self.daemon.Stop()
        self.daemon.join()
        print("exit cv2")

    #end run()

#end class VideoCaptureDaemon


class SimThread(threading.Thread):
    def __init__(self):
        super().__init__()

        self.bStop = False
        self.active = False

        #self.data[0:256, 0:256] = [255, 0, 0] # red patch in upper left
    #end __init__()

    def Stop(self):
        self.bStop = True
        #World.bStop = True
        World.Stop()
        while(self.active):
            time.sleep(1)
    #end Stop()

    def run(self):
        self.active = True
        while(not self.bStop):

            try:
                if(not World.Next()):
                    time.sleep(0.5)

            except Exception as e:
                print('ERR: '+ str(e))
                print("Can't read frame, reconnect")
            #end try/expect

            #time.sleep(0.1)
        #end while()
        self.active = False
        print("exit st")

    #end run()

#end class SimThread
