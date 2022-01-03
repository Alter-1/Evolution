# // _AT_ 110821 16:23 

# OutputDebugString/printX/etc

import sys
# its win32, maybe there is win64 too?
is_windows = sys.platform.startswith('win')
if is_windows:
    from win32api import OutputDebugString
#end if is_windows

def _OutputDebugString(x):
    OutputDebugString(str(x))

if is_windows:
    handlers = [print, _OutputDebugString]
else:
    handlers = [print]
#end if is_windows

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
