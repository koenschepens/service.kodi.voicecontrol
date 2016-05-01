import sys
import time

import kodi
from media_base import MediaBase
#from kodiContextFiles.KeyPad import KeyPad

try:
    import xbmcgui
    import xbmcplugin
    import xbmc, xbmcaddon
except:
    sys.path.append('/usr/share/pyshared/xbmc')
    try:
        from xbmcclient import XBMCClient,ACTION_EXECBUILTIN,ACTION_BUTTON
        import xbmcgui
        import xbmcplugin
        import xbmc, xbmcaddon
    except:
        class xbmc():
            LOGDEBUG = 0
            LOGWARNING = 1
            LOGERROR = 2

        WINDOW_DIALOG_TEXT_VIEWER = 4
        pass

class Kodi(MediaBase):
    Config = None
    def __init__(self, context):
        MediaBase.__init__(self, context)
     
    def log(self, text, logType = "warning"):
        logTypes = { 
            "debug": xbmc.LOGDEBUG,
            "error": xbmc.LOGERROR,
            "warning": xbmc.LOGWARNING
        }

        xbmc.log(msg= "[state: " + self.context.state.__class__.__name__ + "]: " + text, level=logTypes[logType])

    def show_notification(self, title, message = ''):
        dialog = xbmcgui.Dialog()
        dialog.notification(title, message, xbmcgui.NOTIFICATION_INFO, 5000)

    def show_text(self, title):
        self.activate_window(WINDOW_DIALOG_TEXT_VIEWER)

    def get_json_result(self, query):
        xbmcResult = self.context.xbmc.executeJSONRPC(query.encode('utf8'))

        if(self.context.log(xbmcResult['status']['code'] == '200')):
            self.context.log("succes! " + str(xbmcResult))
        else:
            self.context.log("error! result.ParsedJson: " + str(xbmcResult.ParsedJson) + ". Kodi response: " + str(xbmcResult))

        return xbmcResult

    def activate_window(self, pluginurl = None, window = 'videos'):
        if(pluginurl is None):
            action = 'ActivateWindow(' + window + ')'
        else:
            action = 'ActivateWindow(' + window + ',' + pluginurl + ')'

        self.send_action(action)
        
        container = kodi.Container()
        container.load()
        container.updateItems()

        return container

    def send_action(self, action):
        self.log("sending action: " + action)
        xbmc.executebuiltin(action)

    def show_notification(self, title, message = ''):
        self.media_engine.show_notification(title, message)

    def user_input_required(self):
        return self.media_engine.user_input_required()

    def play_youtube_video(self, url):
        self.activate_window("videos","plugin://plugin.video.youtube/kodion/search/query/?q={q}")

    def search_youtube_video(self, q):
        self.activate_window("videos","plugin://plugin.video.youtube/kodion/search/query/?q=" + q)

    def play_movie(self, result):
        params = result.Parameters
        if('title' in params and params['title'] != '$title'):
            q = params['title']
            self.media_engine.search_movie(q)
            url = 'plugin://plugin.video.kodipopcorntime/search?query=' + q + ''
        elif('searchQuery' in params and params['searchQuery'] != '$q'):
            q = params['searchQuery']
            url = 'plugin://plugin.video.kodipopcorntime/search?query=' + q + ''
        elif('genre' in params and params['genre'] != '$genre'):
            url = 'plugin://plugin.video.kodipopcorntime/genres/' + params['genre'] + '/1?limit=20'
        else:
            url = "plugin://plugin.video.kodipopcorntime/genres"

        container = self.context.activate_window(url, window='videos')

    def show_weather(self, location):
        self.activate_window(pluginurl = None, window = "weather")

    def user_input_required(self):
        self.log("check if user input is required")
        time.sleep(8)
        win = xbmcgui.WindowDialog()

        #self.log("controlList.size: " + str(controlList.size()))
        numberOfItems = int(xbmc.getInfoLabel("Container().NumItems"))

        items = []

        for i in xrange(1,numberOfItems):
            skip = 0
            label = xbmc.getInfoLabel("Container().ListItem(" + str(i) + ").Label")
            items.append({ "label": label, "number" : i })

        mydisplay = KeyPad()
        mydisplay.addItems(items)
        mydisplay.doModal()

            #win.setProperty("Container().ListItem(" + str(i) + ").Label", "[" + str(i) + "] " + label )
        return numberOfItems > 1

    def get_show_notification_json(self, title, message, id):
        return '{ "jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": { "title": "' + title + '", "message": "' + message + '" }, "id": ' + str(id) + ' }'
