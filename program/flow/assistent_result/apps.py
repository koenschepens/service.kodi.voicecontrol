from program.flow.assistent_result import AssistentResult

__author__ = 'macbook'
class AppsResult(AssistentResult):
    app_name = None
    def __init__(self, app_name):
        self.app_name = app_name