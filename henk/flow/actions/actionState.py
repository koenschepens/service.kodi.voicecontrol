from ..actions import spotify_action
from ..states.statebase import StateBase
import media, news, input as Input, images, apps, wisdom
import name, weather, clock, message, smalltalk
from configActionState import configActionState as cs

class actionState(StateBase):
    def handle(self, result):
        if(hasattr(result.action, '__call__')):
            result.action(result)
        else:
            immediateActions = self.context.config.options("immediateActions")

            if(isinstance(result, basestring)):
                self.context.state = cs(self.context)
                self.context.state.handle(result)
                return

            configState = cs(self.context)

            if(not configState.handle(result)):
                self.context.log(result.action + " is not a config item")

                self.context.log("Action: " + str(result.action))

                actionItems = result.action.split('.')
                actionClasses = {
                    "music": spotify_action.spotifyState,
                    "media": media.media,
                    "wisdom": wisdom.wisdom,
                    "smalltalk": smalltalk.smalltalk,
                    "weather": weather.weather,
                    "news": news.news,
                    "input": Input.input,
                    "images": images.images,
                    "message": message.message,
                    "clock": clock.clock,
                    "name": name.name,
                    "apps": apps.apps
                }

                if(actionItems[0] in actionClasses):
                    self.context.log("domain exists: " + actionItems[0])
                    self.context.state = actionClasses[actionItems[0]](self.context)
                else:
                    self.context.log("domain " + actionItems[0] + " does not exist. Using config")
                    self.context.state = cs(self.context)

                if(hasattr(self.context.state, actionItems[1])):
                    self.context.log("actionState action: " + actionItems[1])
                    action = getattr(self.context.state, actionItems[1])
                    action(result)
                else:
                    self.context.log("action does not exist: " + actionItems[1] + ". Using " + self.context.state.__class__.__name__ + ".handle()")
                    self.context.state.handle(result)

        # Check if user input is required
        if(self.context.user_input_required()):
            self.context.state = input(self.context)
            self.context.state.handle(result)


