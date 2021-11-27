# // _AT_ 110821 16:23 

# OutputDebugString/printX/etc

from win32api import OutputDebugString

def _OutputDebugString(x):
    OutputDebugString(str(x))

handlers = [print, _OutputDebugString]
global_prefix = "Python"

def printX(msg):
    #global gui
    #global lg
    global handlers
    #global regOutpuDebStr
    #if(regOutpuDebStr == 0):
    #lg = logging.getLogger()

    #lg.addHandler(DbgViewHandler())
    #    regOutpuDebStr = 1

    #lg.warning(str)

#    if(gui == 0):
#        print("SipLinpho: "+str)
#        return
    #PrintLog(str)
    for print_f in handlers:
        print_f(msg)
    #lg.info("SipLinpho: "+str)
    #OutputDebugString(str)

# end printX

class ODSWrap:
    def __init__(self, prefix="Python"):
        self.prefix = prefix
#        self.gui = gui
    
    def printW(self, msg):
        global global_prefix
        s = ""
        if(global_prefix != None):
            s = s + global_prefix+": "
        if(self.prefix != None):
            s = s + self.prefix+": "
        printX(s+str(msg))
        #self.gui.update_idletasks()
