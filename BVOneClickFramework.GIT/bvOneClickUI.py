
class BVOneClickMessageLog (object):

    def stdout(self, msg): print self.__source +'>  '+ msg
    def stderr(self,msg): self.stdout (msg)

    def __init__(self, prefix):
        self.__source = prefix


class BVOneClickUI (object):
    'singletone representing the UI'

    #  methods to be defined in subclasses
    def initialize (self, talkjobs): pass
    'intialize the UI with the list of talks and regiter a UI event handler on the talks'

    def __init__(self):
        return

""" thisa is not necessary.
class UIHandle :
    ' inte UI handle are the UI coordinates used to render the talk infomrmation on the uI\
    this will be stored in the instance of event handlers registered in the talk events'

class UITalkEventHandler : (DBTalkEventHandler)

    def __init__(self, uh):
        __uihandle = uh
"""






