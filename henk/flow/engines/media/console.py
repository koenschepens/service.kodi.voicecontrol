import media_base

try:
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

class Console(media_base.MediaBase):
    pass
