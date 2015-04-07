
"""
|The way the code is designed is not about having a UI or DB modules. There is another system out there that
laod  the database in some way. Try to call it in a different way.
"""
class BVOneClickMessageLog (object):

    def stdout(self, msg): print self.__source +'>  '+ msg
    def stderr(self,msg): self.stdout (msg)

    def __init__(self, prefix):
        self.__source = prefix







