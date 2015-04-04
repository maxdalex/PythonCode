from bvOneClickCT import *
from bvOneClickDB import *
from bvOneClickUI import *

#### module confuguration ########
_log = BVOneClickMessageLog('mp4MediaProc')

class MP4MediaProcAgent (BVMediaProcAgent):
    def processMedia(self):
        _log.stdout("No processing coded")
        return

    def __init__(self, key, ds):
        super(MP4MediaProcAgent, self).__init__(key, ds)