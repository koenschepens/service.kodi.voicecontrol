import logging

import target_base
import includes.xbmc_client.xbmc_client as xbmcclient


# Use this context to create a remote connection with target
class KodiRemote(target_base.TargetBase):
    def __init__(self, context):
        target_base.TargetBase.__init__(self, context)

        host = self.context.config.get("xbmc", "host")
        port = self.context.config.getint("xbmc", "port")
        self.client = xbmcclient.XBMCClient()
        self.client.connect(host, port)

    def log(self, message):
        if(self.client is not None):
            self.client.send_log(3, message)
        logging.log(1, message)

    def activate_window(self, pluginurl = None, window = 'videos'):
        if(pluginurl is None):
            action = 'ActivateWindow(' + window + ')'
        else:
            action = 'ActivateWindow(' + window + ',' + pluginurl + ')'
        self.send_action(action)

    def send_action(self, action):
        self.log("sending action: " + action)
        self.client.send_action(action, xbmcclient.ACTION_EXECBUILTIN)

    def show_notification(self, title, message = ''):
        self.log("sending notification: " + title + "," + message)        
        self.client.send_notification(title=title, message=message, icon_file=None)

    def get_window(self):
        return None

    def user_input_required(self):
        return False
        '''win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        numberOfItems = xbmc.getProperty("Container().NumItems")
        if(numberOfItems > 9):
            numberOfItems = 9
        for i in xrange(1,numberOfItems):
            label = xbmc.getProperty("Container().ListItem(" + str(i) + ").Label")
            xbmc.setProperty("Container().ListItem(" + str(i) + ").Label", "[" + str(i) + "] " + label )
        return numberOfItems > 1'''

    
