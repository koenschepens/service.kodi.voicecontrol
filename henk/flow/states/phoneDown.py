import time

import statebase
import phoneUp


class PhoneDown(statebase.StateBase):
    def go(self):
        time.sleep(0.25)

        while (not self.context.is_up(False)):
            time.sleep(0.25)

        self.context.state = phoneUp.PhoneUp(self.context)
        self.context.state.go()