import sys

from ..states.statebase import StateBase


class weather(StateBase):

    def handle(self, result):
        self.context.log(str(result.Parameters))

    def search(self, result):
        self.context.show_weather(result.Parameters["location"])
        self.context.say(result.Text)

    def search_old(self, result):
        self.context.log("weather search: " + str(result.Parameters))

        if("location" in result.Parameters):
            #try:
            sys.path.append('/home/osmc/.target/addons/weather.yahoo/')
            sys.path.append('/home/osmc/.target/addons/weather.yahoo/resources/lib')

            #self.ContextBase.ActivateWindow(pluginurl = None, window = "weather")
            locname = result.Parameters["location"]
            locid = find_location(locname)
            forecast(locname, locid)
            #except:
            #    self.ContextBase.log("error loading weather")
            #    self.ContextBase.ActivateWindow(pluginurl = None, window = "weather")
        else:
            self.context.activate_window(pluginurl = None, window = "weather")
