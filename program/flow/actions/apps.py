import ConfigParser

from program.flow.states.statebase import StateBase

try:
    import xbmcgui
except:
    pass

class apps(StateBase):

    def handle(self, result):
        self.config = ConfigParser.RawConfigParser()
        configFile = 'actions.config'
        self.log(configFile)
        self.config.read(configFile)

    def open(self, result):
        if(result.app_name is None):
            result.app_name = self.context.ask(result.assistent_response)

        if(result.app_name in self.context.config.options("apps")):
            appId = self.context.config.get("apps", result.app_name)
            self.context.log("open app: " + appId)
            self.context.open_plugin(pluginurl = appId)



       