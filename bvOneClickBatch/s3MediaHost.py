from ocuModel import *
from ocuUtils import *

_log = BVOneClickMessageLog('S3MediaHostAgent')



class S3VideoMediumHostAgent(BVMediumHostAgent):
     def __initSubclass(self, key, thumb, ds):
         _log.stderr(' created for Talk %s'%(self.getTalk().getID()))

     def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: video not uploaded')


class S3AudioMediumHostAgent(BVMediumHostAgent):
     def  __initSubclass(self, key, thumb, ds):
          _log.stderr(' created for Talk %s'%(self.getTalk().getID()))

     def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: video not uploaded')
