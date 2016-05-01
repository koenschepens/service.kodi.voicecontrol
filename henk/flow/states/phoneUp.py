import random
from time import sleep

from flow.actions.actionState import actionState
import statebase
import phoneDown


class PhoneUp(statebase.StateBase):
    def go(self):
        while(self.context.is_up(False)):
            if(self.context.is_talking()):
                self.context.log("Please wait... Still talking...")
                while(self.context.is_talking()):
                    sleep(0.5)

            '''questionid = random.choice(self.context.config.options("questions"))
            question = self.context.config.get("questions", questionid)
            self.context.log(question)
            result = self.context.ask(question)'''

            result = self.context.ask()

            if(result is not None):
                self.context.state = actionState(self.context)
                self.context.state.handle(result)

                if(result.SpokenResponse is not None):
                    # also speak out the result
                    self.context.say(result.SpokenResponse, "phone_out", False)

        self.context.state = phoneDown.PhoneDown(self.context)
        self.context.state.go()


        

