from bvOneClickMD import *
from bvOneClickUtils import *

_log = BVOneClickMessageLog('S3MediaHostAgent')



class S3VideoMediaHostAgent(BVMediaHostAgent):
     def __initSubclass(self, key, thumb, ds):
        _log.stderr(' created for Talk %s'%(self.getTalk().getID()))

     def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: video not uploaded')


class S3AudioMediaHostAgent(BVMediaHostAgent):
     def __initSubclass(self, key, thumb, ds):
         _log.stderr(' created for Talk %s'%(self.getTalk().getID()))

    def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: video not uploaded')
