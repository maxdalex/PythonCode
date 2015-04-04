from bvOneClickDB import *
from bvOneClickUI import *


#### module confuguration ########
_log = BVOneClickMessageLog('vimeoHostAgent')

class VimeoMediaHostAgent (BVMediaHostAgent):

    def __init__(self, key, thumb, ds):
     super(VimeoMediaHostAgent, self).__init__(key, thumb,ds)

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

