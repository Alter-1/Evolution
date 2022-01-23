import tkinter as tk
from tkinter import *
from tkinter import ttk
#from tkinter as tk
from ttkthemes import ThemedTk
from DlgBase import *

class WorldOptions(DlgBase):
    def __init__(self, parent, o):
        DlgBase.__init__(self, parent, o, 'World global options')
        #parent.wm_attributes("-disabled", True)
        '''
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

        commonframe = self.root_label = LabelFrame(root, text='World global options')
        commonframe.grid(column = 0, row = 0)
        commonframe.configure(background='black',foreground='green')
        varlist = self.varlist = dict()
        '''
        commonframe = self.root_label
        row = 1
        varlist = self.varlist

        for name in o.Tunable:
            v = getattr(o, "g"+name)
            title, defv = o.Tunable[name]
            lb  = ttk.Label(commonframe, text=title)
            lb.grid(column = 1, row = row, sticky=W)
            if(isinstance(defv, bool) or isinstance(v, bool)):
                x_var = tk.IntVar(commonframe, int(v))
                chk = ttk.Checkbutton(commonframe, variable=x_var).grid(column = 0, row = row,sticky=W, padx=8, pady=5)
            elif(isinstance(defv, int)):
                txtv = str(v)
                x_var = tk.StringVar(commonframe, txtv)
                txt = tk.Entry(commonframe, textvariable=x_var, width=5).grid(column = 0, row = row,sticky=W, padx=8, pady=5)
                x_var.set(txtv)
            elif(isinstance(defv, dict)):
                txtv = str(defv[v])
                x_var = tk.StringVar(commonframe, txtv)
                cb = ttk.Combobox(commonframe, textvariable=x_var, values=list(defv.values()))
                cb.grid(column = 0, row = row,sticky=W, padx=8, pady=5)
            varlist[name] = x_var
            row += 1
        #end for(o.Tunable)

        self.btSahre = ttk.Button(commonframe, text = "Apply",  command = self.Apply ).grid( column = 0, row = row,sticky=W, padx=8, pady=5)
        self.btAgg   = ttk.Button(commonframe, text = "Cancel", command = self.Cancel).grid( column = 1, row = row,sticky=W, padx=8, pady=5)
        self.btReset = ttk.Button(commonframe, text = "Reset",  command = self.Reset ).grid( column = 2, row = row,sticky=W, padx=8, pady=5)

        '''
        # This is watching the window manager close button
        # and uses the same callback function as the other buttons
        # (you can use which ever you want, BUT REMEMBER TO ENABLE
        # THE PARENT WINDOW AGAIN)
        root.protocol("WM_DELETE_WINDOW", self.Close_Toplevel)
        root.update_idletasks()
        # a trick to activate the window (on windows 7)
        root.deiconify()
        print("init done");
        '''

    def Apply(self, event=None):
        print("Apply");

        o = self.World
        varlist = self.varlist
        for name in o.Tunable:
            v = getattr(o, "g"+name)
            title, defv = o.Tunable[name]
            x_var = varlist[name]
            if(isinstance(defv, bool) or isinstance(v, bool)):
                v = (x_var.get() == 1)
            elif(isinstance(defv, int)):
                v = int(x_var.get())
            elif(isinstance(defv, dict)):
                sv = x_var.get()
                for v in defv:
                    if(defv[v] == sv):
                        break
            setattr(o, "g"+name, v)
        #end for(o.Tunable)

        self.returning = True
        self.root.quit()
    '''
    def Cancel(self, event=None):
        print("Cancel");
        #self.returning = self.b2_return
        self.returning = False
        self.root.quit()
    '''
    def Reset(self, event=None):
        print("Reset");

        o = self.World
        varlist = self.varlist
        for name in o.Tunable:
            v = getattr(o, "g"+name)
            title, defv = o.Tunable[name]
            x_var = varlist[name]
            if(isinstance(defv, bool) or isinstance(v, bool)):
                x_var.set(int(v))
            elif(isinstance(defv, int)):
                x_var.set(str(v))
            elif(isinstance(defv, dict)):
                x_var.set(str(v))
        #end for(o.Tunable)

    '''
    def Close_Toplevel(self):

        print("Close_Toplevel");
        # a trick to activate the window (on windows 7)
        self.root.deiconify()
        self.returning = False
    '''

    def Show(parent, o):
        dlg = WorldOptions(parent, o)
        dlg._Show()
        '''
        print("start root.mainloop()");
        dlg.root.mainloop()
        print("end root.mainloop()");
        dlg.root.destroy()
        return dlg.returning
        '''

#end class WorldOptions

