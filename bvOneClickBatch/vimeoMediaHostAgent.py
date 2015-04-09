from ocuModel import *
from ocuUtils import *


#### module confuguration ########
_log = BVOneClickMessageLog('vimeoHostAgent')

class VimeoMediumHostAgent (BVMediumHostAgent):

    def __initSubclass(self, key, thumb, ds):
     _log.stderr(' created for Talk %s'%(self.getTalk().getID()))

    def upload(self):
        _log.stderr('Talk %s: hosting not yet implemented'%(self.getTalk().getID()))
        self._dispatchFailure('ERROR: video not uploaded')


#####################################################

YOUR_API_TOKEN = 12345
YOUR_TOKEN_SECRET = 12345

# I think to specify the channel we need to set an end point. Not clear how to do it but there i an example in github

if __name__ == '__main__':

    import vimeo

    v = vimeo.VimeoClient(
        key=YOUR_API_TOKEN,
        secret=YOUR_TOKEN_SECRET)

    video_uri = v.upload('D:\Massimo\MyDocuments\RECOVERY\BalancedView\Service\OneClickUpload\TestData\TESTYouTube.mp4')
    print video_uri

