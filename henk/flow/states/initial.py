import sys

import statebase
import phoneDown
import phoneUp

reload(sys) 
sys.setdefaultencoding('UTF8')

class Initial(statebase.StateBase):
    def __init__(self, context):
        self.context = context

    def go(self):
        if(self.context.is_up(True)):
            self.context.state = phoneUp.PhoneUp(self.context)
        else:
            self.context.state = phoneDown.PhoneDown(self.context)
        
        self.context.state.go()