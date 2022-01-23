import tkinter as tk
from tkinter import *
from tkinter import ttk
#from tkinter as tk
from ttkthemes import ThemedTk

class DlgBase(object):
    def __init__(self, parent, o, labelText):
        #parent.wm_attributes("-disabled", True)
        self.parent = parent
        self.World = o

        # Creating the toplevel dialog
        root = self.root = tk.Toplevel(parent)

        style = ttk.Style()
        style.theme_use('black')
        style.configure('TButton', background = 'Black', foreground = 'Lime')#, width = 20, borderwidth=1, focusthickness=3, focuscolor='none')
        #style.configure()
        #style.map('TButton', background=[('active','red')])
        root.configure(background='black')

        root.minsize(300, 100)
        root.resizable(False, False)
        root.grab_set() # modal

        # Tell the window manager, this is the child widget.
        # Interesting, if you want to let the child window 
        # flash if user clicks onto parent
        self.root.transient(parent)

        commonframe = self.root_label = LabelFrame(root, text=labelText)
        commonframe.grid(column = 0, row = 0)
        commonframe.configure(background='black',foreground='green')

        row = 1
        varlist = self.varlist = dict()

        # This is watching the window manager close button
        # and uses the same callback function as the other buttons
        # (you can use which ever you want, BUT REMEMBER TO ENABLE
        # THE PARENT WINDOW AGAIN)
        root.protocol("WM_DELETE_WINDOW", self.Close_Toplevel)
        root.update_idletasks()
        # a trick to activate the window (on windows 7)
        root.deiconify()
        print("init done");
    #end __init__()

    def Cancel(self, event=None):
        print("Cancel");
        #self.returning = self.b2_return
        self.returning = False
        self.root.quit()
    #end Cancel()

    def AddInput(self, v, x, y):
        commonframe = self.root_label
        txtv = str(v)
        x_var = tk.StringVar(commonframe, txtv)
        txt = tk.Entry(commonframe, textvariable=x_var, width=5).grid(column = x, row = y,sticky=W, padx=8, pady=5)
        x_var.set(txtv)
        return x_var
    #end AddInput()

    def Close_Toplevel(self):

        print("Close_Toplevel");
        # a trick to activate the window (on windows 7)
        self.root.deiconify()
        self.returning = False
    #end Close_Toplevel()

    def _Show(self):
        print("start root.mainloop()");
        self.root.mainloop()
        print("end root.mainloop()");
        self.root.destroy()
        return self.returning
    #end _Show()

#end class DlgBase

