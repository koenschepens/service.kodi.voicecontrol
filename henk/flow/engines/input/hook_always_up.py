from console import Console

class HookAlwaysUp(Console):
    def is_up(self):
        return True