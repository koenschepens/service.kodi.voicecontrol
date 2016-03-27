__author__ = 'macbook'

class Google():
    def __init__(self, context):
        self.Language = context.Language
        self.IncludesDir = context.IncludesDir
        self.context = context

    def get(self):
        return self.context.execute_script(self.IncludesDir + 'speech-recog.sh -l ' + self.Language).strip('"')
