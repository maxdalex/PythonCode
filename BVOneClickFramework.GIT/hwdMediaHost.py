from bvOneClickDB import *
from bvOneClickUI import *


##################### ON THUMBNAIL FILES for AUDIOS ##############################
# Thumbnails files for the HWD audio galleries are stored on the server and need to be specified as links
# at upload time. THis is the reason why a dictionary of trainer/links is passed to the constructor of the agent
# Still a possibility that the links can be giessed knowin the name of ht etrainwer rather than explicitely stored.
# Check with Anja

_log = BVOneClickMessageLog('HWDHostAgent')

class HWDVideoMediaHostAgent(BVMediaHostAgent):

    def __init__(self, key, thumb, ds):
     super(HWDVideoMediaHostAgent, self).__init__(key, thumb,ds)

    def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: video not uploaded')

class HWDAudioMediaHostAgent(BVMediaHostAgent):

    def __init__(self, key, thumbDict, ds):
     super(HWDAudioMediaHostAgent, self).__init__(key, thumbDict,ds)

    def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: audio not uploaded')

