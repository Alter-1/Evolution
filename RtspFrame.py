import tkinter as tk 

import World
from World import L
from World import T

from tkinter import *
from tkinter import ttk
from selenium.webdriver.support.expected_conditions import number_of_windows_to_be
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
        self.canvas.grid(row=1, column=1)
        # Update image on canvas
        window.after(self.interval, self.update_image)
        self.button = ttk.Button()
        
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

# end class VideoStreamWindow

def crop_center(img,cropx,cropy):
    y,x,c = img.shape
    startx = x//2 - cropx//2
    starty = y//2 - cropy//2    
    return img[starty:starty+cropy, startx:startx+cropx, :]

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
        World.CreateMatrix(w, h, 2500)

        self.daemon = SimThread()
        #self.daemon.start()

    def Stop(self):
        self.stop = True
        self.daemon.Stop()

    def NextFrame(self):
        #World.Next()

        if(self.prev_mode == self.mode and self.prev_epoch == World.gEpoch):
            return None

        self.prev_mode = self.mode    
        self.prev_epoch = World.gEpoch

        for x in range(self.w):
            for y in range(self.h):

                g = 0
                r = 0
                b = 0
                if(self.mode == 0 or self.mode == L.age):

                    if(World.gMatrix[x,y, L.ctype] == T.ground):
                        g = 50+int(World.gMatrix[x,y, L.resources]*1.5)
                    else:
                        #print("@"+str(x)+"x"+str(y))
                        if(World.gMatrix[x,y, L.sex] == T.male):
                            b = 250-World.gMatrix[x,y, L.age]*2
                        else:
                            r = 250-World.gMatrix[x,y, L.age]*2
                        g = 50 + int(World.gMatrix[x,y, L.energy]*1.5)
                
                #if(self.mode > L.age):
                else:
                    if(World.gMatrix[x,y, L.ctype] == T.person):

                        '''
                        if(self.mode == 1):
                            v = World.gMatrix[x,y, L.energy]
                        if(self.mode >= L.genes):
                            v = World.gMatrix[x,y, self.mode]
                        '''

                        v = World.gMatrix[x,y, self.mode]*2
                        if(World.gMatrix[x,y, L.sex] == T.male):
                            b = 50+v
                        else:
                            r = 50+v

                        g = 50 + v


                rgb = [r, g, b]
                self.data[x*2,y*2] = rgb
                self.data[x*2+1,y*2] = rgb
                self.data[x*2,y*2+1] = rgb
                self.data[x*2+1,y*2+1] = rgb

        return self.data

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

#end class VideoCaptureDaemon()


class SimThread(threading.Thread):
    def __init__(self):
        super().__init__()

        self.bStop = False
        self.active = False

        #self.data[0:256, 0:256] = [255, 0, 0] # red patch in upper left
    def Stop(self):
        self.bStop = True
        World.bStop = True
        while(self.active):
            time.sleep(1)

    def run(self):
        self.active = True
        while(not self.bStop):

            try:
                World.Next()
            except Exception as e:
                print('ERR: '+ str(e))
                print("Can't read frame, reconnect")
            #end try/expect

            #time.sleep(0.1)
        #end while()
        self.active = False
        print("exit st")
