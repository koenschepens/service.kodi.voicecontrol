from media_command_base import MediaCommand

__author__ = 'macbook'
class AppsResult(MediaCommand):
    app_name = None
    def __init__(self, app_name):
        self.app_name = app_name