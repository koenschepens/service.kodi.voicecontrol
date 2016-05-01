from console import Console

class HookAlwaysUp(Console):
    active = False
    def is_up(self, initial = False):
        if(not self.active and not initial):
            self.active = True
            return True
        else:
            return not self.active