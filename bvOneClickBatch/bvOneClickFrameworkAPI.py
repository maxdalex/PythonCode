from  bvOneClickCT import *
from  bvOneClickMD import *
from youtubeMediaHostAgent import *
from vimeoMediaHostAgent import *
from hwdMediaHost import *
from s3MediaHost import *
from mp3id3MediaProcAgent import *
from mp4MediaProcAgent import *
from gSheetJobManager import *

#Agents Keys
YOUTUBE = 'youtube'
VIMEO = 'vimeo'
HWDVIDEO = 'hwdvideo'
HWDAUDIO = 'hwdaudio'
S3VIDEO = 's3video'
S3AUDIO = 's3audio'

# Factory Methods for Agents  creation
def createAudioSrcProcAgent(key,directives): return MP3ID3SMediumProcAgent(key, directives)

def createVideoSrcProcAgent(key,directives): return MP4MediumProcAgent(key,directives)

def createHostAgent(akey, videothumb, directives):
    if akey == YOUTUBE: return  YoutubeMediaHostAgent(akey, videothumb, directives)
    if akey == VIMEO: return    VimeoMediaHostAgent(akey, videothumb, directives)
    if akey == HWDAUDIO: return HWDAudioMediaHostAgent(akey, videothumb, directives)
    if akey == HWDVIDEO: return HWDVideoMediaHostAgent(akey, videothumb, directives)
    if akey == S3AUDIO: return  S3AudioMediaHostAgent(akey, videothumb, directives)
    if akey == S3VIDEO: return  S3VideoMediaHostAgent(akey, videothumb, directives)


################################ Framework Configuration ##################################################
# If the main of the system is in the Job Manager than this is the class to use in it.

class BVOneClickFramework(object):

    def processJob(self, talk):
         BVControlProcess.processJob(talk)

    def __init__(self):
        #set the factory methods to create agents
        OcuModelFactory.videoPaFactoryMethod = createAudioSrcProcAgent
        OcuModelFactory.audioPaFactoryMethod = createAudioSrcProcAgent
        OcuModelFactory.haFactoryMethod = createHostAgent



