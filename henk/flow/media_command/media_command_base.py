class ImmediateResult:
    def executeAction(self, action):
        #{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"down"},"id":1}
        return '{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"' + action + '"},"id":1}'

class MediaCommand():
    Id = 0
    NextFunction = None
    NeedsUserInput = False
    action = {}
    IncludesDir = None
    ResolvedQuery = None
    Text = None
    action = None
    Parameters = {}
    Url = None
    SpokenResponse = None
    OriginalResult = ''

    def __init__(self, domain, domain_action, *args, **kwargs):
        self.action = domain + "." + domain_action

    @property
    def get_domain(self):
        return self.action.split('.')[0] if self.action is not None else None

    @property
    def get_domain_action(self):
        return self.action.split('.')[1] if self.action is not None else None

    def updateParams(self, params):
        paramsDict = {}

        for n, param in enumerate(params):
            splitted = params[n].split('=')
            name = splitted[0]
            value = splitted[1]

            for p in self.Parameters:
                value = value.replace("$" + p, self.Parameters[p])

            if("title" in self.Parameters):
                value = value.replace("$q", self.Parameters["title"])
                value = value.replace("$title", self.Parameters["title"])
                value = value.replace("$service_name", 'popcorntime')

            value = value.replace("$speech", self.Text)
            value = value.replace("$resolvedQuery", self.ResolvedQuery)

            paramsDict[name] = value

        return paramsDict

    def __str__(self):
        result = ""
        for slot in dir(self):
            if(not slot.startswith('_')):
                attr = getattr(self, slot)
                result = result + "\r\n" + slot + ": " + str(attr)
        return result