from time import sleep

from program.flow.actions.actionState import actionState
import statebase
import phoneDown


class PhoneUp(statebase.StateBase):
    def go(self):
        while(self.context.isUp()):
            if(self.context.is_talking()):
                self.context.log("Please wait... Still talking...")
                while(self.context.is_talking()):
                    sleep(0.5)

            result = self.context.ask()

            self.context.state = actionState(self.context)
            self.context.state.handle(result)

            if(result.SpokenResponse is not None):
                # also speak out the result
                self.context.say(result.SpokenResponse, "phone_out", False)

        self.context.state = phoneDown.PhoneDown(self.context)
        self.context.state.go()


        

