from ods import ODSWrap
import AsyncTTKQ

lg = ODSWrap("AsyncTextBox")
printX = lg.printW

class AsyncTextBox(AsyncTTKQ.AsyncTTKQ):

    def __init__(self, gui, PrintTextBoxReal):
        super().__init__(gui, PrintTextBoxReal)
    #end __init__

    def PrintTextBox(self, myStr):
        self.DoAction(myStr)
    # end PrintTextBox()

# end class AsyncTextBox

