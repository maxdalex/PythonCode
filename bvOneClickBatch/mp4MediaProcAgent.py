from ocuControl import *
from ocuModel import *
from ocuUtils import *

#### module confuguration ########
_log = BVOneClickMessageLog('mp4MediaProc')

class MP4MediumProcAgent (BVMediumProcAgent):
    def processMedium(self):
        _log.stdout("No processing coded")
        return

    def __init__(self, key, ds):
        super(MP4MediumProcAgent, self).__init__(key, ds)