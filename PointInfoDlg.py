import tkinter as tk
from tkinter import *
from tkinter import ttk
#from tkinter as tk
from ttkthemes import ThemedTk
from DlgBase import *
from WorldConst import L, T, LayerName

class PointInfoDlg(DlgBase):
    def __init__(self, parent):
        DlgBase.__init__(self, parent, None, 'Inspect location')

        commonframe = self.root_label
        row = 1
        varlist = self.varlist

        lb  = ttk.Label(commonframe, text="--- Value ---")
        lb.grid(column = 0, row = row, sticky=W)

        lb  = ttk.Label(commonframe, text="--- Name ---")
        lb.grid(column = 1, row = row, columnspan=3, sticky=W)

        row += 1

        for i in range(L.layers):

            name = LayerName[i]

            lb  = ttk.Label(commonframe, text=name)
            lb.grid(column = 1, row = row, columnspan=3, sticky=W)

            x_var = ttk.Label(commonframe, text='')
            x_var.grid(column = 0, row = row, sticky=W)

            varlist[name] = x_var
            row += 1
        #end for(o.Tunable)

        self.btClose = ttk.Button(commonframe, text = "Close",  command = self.Cancel).grid( column = 1, row = row,sticky=W, padx=8, pady=5)
    #end __init__()

    def onClick(self, _item):
        print("click");

        item = list(_item)
        varlist = self.varlist
        ctype = 0
        for i in range(L.layers):
            name = LayerName[i]
            x_var = varlist[name]

            v = item[i]
            if(i == L.resources):
                pass
            elif(i == L.ctype):
                ctype = v
                if(v == T.ground):
                    v = 'ground'
                else:
                    v = ''
            elif(ctype == T.ground):
                if(not i == L.energy):
                    v = ''
            elif(i == L.sex):
                if(v == T.male):
                    v = 'male'
                else:
                    v = 'female'
            elif(i >= L.color):
                color = v
                r = 63 + int(((color & 0xe0) / 256) * 192)
                g = 63 + int(((color & 0x18) / 32 ) * 192)
                b = 63 + int(((color & 0x07) / 8  ) * 192)

                v = '#'+hex((r*256+g)*256+b)

            x_var.config(text=str(v))
            x_var.update()
        #end for(o.Tunable)

    #end onClick()

#end class PointInfoDlg

