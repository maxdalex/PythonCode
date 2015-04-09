from  ocuControl import *
import  ocuModel
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
def createAudioSrcProcAgent(key,directives): return MP3ID3MediumProcAgent(key, directives)

def createVideoSrcProcAgent(key,directives): return MP4MediumProcAgent(key,directives)

def createHostAgent(akey, videothumb, directives):
    if akey == YOUTUBE: return  YoutubeMediumHostAgent(akey, videothumb, directives)
    if akey == VIMEO: return    VimeoMediumHostAgent(akey, videothumb, directives)
    if akey == HWDAUDIO: return HWDAudioMediumHostAgent(akey, videothumb, directives)
    if akey == HWDVIDEO: return HWDVideoMediumHostAgent(akey, videothumb, directives)
    if akey == S3AUDIO: return  S3AudioMediumHostAgent(akey, videothumb, directives)
    if akey == S3VIDEO: return  S3VideoMediumHostAgent(akey, videothumb, directives)


################################ Framework Configuration ##################################################
# If the main of the system is in the Job Manager than this is the class to use in it.

class BVOneClickFramework(object):

    def processJob(self, talk):
         OcuControlProcess.processJob(talk)

    def __init__(self):
        #set the factory methods in MD to create agents
        ocuModel.setMDFactoryMethods(createHostAgent,createAudioSrcProcAgent, createVideoSrcProcAgent)



