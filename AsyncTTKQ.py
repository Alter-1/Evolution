# // _AT_ 230821 09:53 
from ods import ODSWrap
import threading
import queue

lg = ODSWrap("AsyncTTKQ")
printX = lg.printW

class AsyncTTKQ:

    def __init__(self, gui, ActionReal):

        self.gui = gui
        self.bStop = False
        self.ActionReal = ActionReal
        self.mqueue = queue.Queue()
    #end __init__

    def DoAction(self, arg):
        #TextArea.insert(END, '\r\n' + myStr)
        if(self.bStop):
            return

        if threading.current_thread() is threading.main_thread():
            self.ActionReal(arg)
            return

        self.mqueue.put(arg)
    # end DoAction()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.mqueue.qsize(  ):
            if(self.bStop):
                return
            try:
                arg = self.mqueue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                self.ActionReal(arg)
#            except Queue.Empty:
#                # just on general principles, although we don't
#                # expect this branch to be taken in this case
#                return
            except Exception as e:
                printX('ERR: '+ str(e))
                continue

        # end while()

    # end processIncoming()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        if(self.bStop):
            return
        self.processIncoming()
        try:
            self.gui.after(200, self.periodicCall)
        except Exception as e:
            printX('ERR: '+ str(e))
            
    #end periodicCall()

# end class AsyncTTKQ

