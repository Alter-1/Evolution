import tkinter as tk
from tkinter import *
from tkinter import ttk
#from tkinter as tk
from ttkthemes import ThemedTk
from DlgBase import *
from WorldConst import L, LayerName

class WorldInit(DlgBase):
    def __init__(self, parent, o):
        DlgBase.__init__(self, parent, o, 'World init options')

        commonframe = self.root_label
        row = 1
        varlist = self.varlist

        lb  = ttk.Label(commonframe, text="Min")
        lb.grid(column = 0, row = row, sticky=W)
        lb  = ttk.Label(commonframe, text="Max")
        lb.grid(column = 1, row = row, sticky=W)

        row += 1

        for i in range(L.genes, L.pseudo_genes):
            name = LayerName[i]
            print(str(i)+" "+name)
            try:
                desc = getattr(o, name)
                a, b = desc
            except:
                a = 0
                b = 100
            #end try

            lb  = ttk.Label(commonframe, text=name)
            lb.grid(column = 2, row = row, columnspan=3, sticky=W)

            pair = []

            x_var = self.AddInput(a, 0, row)
            pair.append(x_var)

            x_var = self.AddInput(b, 1, row)
            pair.append(x_var)

            varlist[name] = pair
            row += 1
        #end for(o.Tunable)

        name = "N"
        v = getattr(o, name)
        x_var = self.AddInput(v, 0, row)
        varlist[name] = x_var

        lb  = ttk.Label(commonframe, text="Initial population")
        lb.grid(column = 2, row = row, columnspan=3, sticky=W)
        row += 1

        self.btApply = ttk.Button(commonframe, text = "Run",    command = self.Apply ).grid( column = 0, row = row,sticky=W, padx=8, pady=5)
        self.btCancel= ttk.Button(commonframe, text = "Cancel", command = self.Cancel).grid( column = 1, row = row,sticky=W, padx=8, pady=5)
        self.btZIQ   = ttk.Button(commonframe, text = "ZeroIQ", command = self.ZIQ   ).grid( column = 2, row = row,sticky=W, padx=8, pady=5)
        self.btRandom= ttk.Button(commonframe, text = "Random", command = self.Random).grid( column = 3, row = row,sticky=W, padx=8, pady=5)
    #end __init__()

    def Apply(self, event=None):
        print("Apply");

        o = self.World
        varlist = self.varlist
        for i in range(L.genes, L.pseudo_genes):
            name = LayerName[i]
            pair = varlist[name]
            x_a, x_b = pair
            a = max(0, int(x_a.get()))
            b = min(100, int(x_b.get()))

            setattr(o, name, [a, b])
        #end for(o.Tunable)

        name = "N"
        x_var = varlist[name]
        v = max(0, int(x_var.get()))
        setattr(o, "N", v)

        print(o)

        self.returning = True
        self.root.quit()
    #end Apply()

    def ZIQ(self, event=None):
        print("zIQ");

        o = self.World
        varlist = self.varlist
        for i in range(L.genes, L.pseudo_genes):
            name = LayerName[i]
            pair = varlist[name]
            x_a, x_b = pair
            if(i == L.share or i == L.fert):
                a = 0
                b = 100
            else:
                a = b = 0

            x_a.set(str(a))
            x_b.set(str(b))

        #end for(o.Tunable)
    #end ZIQ()

    def Random(self, event=None):
        print("zIQ");

        o = self.World
        varlist = self.varlist
        for i in range(L.genes, L.pseudo_genes):
            name = LayerName[i]
            pair = varlist[name]
            x_a, x_b = pair
            a = 0
            b = 100

            x_a.set(str(a))
            x_b.set(str(b))

        #end for(o.Tunable)
    #end Random()

    def Show(parent, o):
        dlg = WorldInit(parent, o)
        return dlg._Show()
        '''
        print("start root.mainloop()");
        dlg.root.mainloop()
        print("end root.mainloop()");
        dlg.root.destroy()
        return dlg.returning
        '''
    #end Show()

#end class WorldInit

