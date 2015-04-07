
from  gSheetJobManager import *
from  mp3id3MediaProcAgent import *
from  mp4MediaProcAgent import *
from  bvOneClickCT import *

################################ Framework Configuration ##################################################
class BVOneClickConf:
    'singletone  factory to provide the concrete instance of the framework'

    YOUTUBE = 'youtube'
    VIMEO = 'vimeo'
    HWDVIDEO = 'hwdvideo'
    HWDAUDIO = 'hwdaudio'
    S3VIDEO = 's3video'
    S3AUDIO = 's3audio'

    @staticmethod
    def getJobManager(): return GSheetJobManager()

    @staticmethod
    def getDB(): return GSheetJobManager()
    @staticmethod
    def getUI(): return UIgspread()
    @staticmethod
    def getCT(): return BVControlProcess()

    # Agents Creation
    @staticmethod
    def createAudioSrcProcAgent(key,directives): return MP3ID3SMediumProcAgent(key, directives)

    @staticmethod
    def createVideoSrcProcAgent(key,directives): return MP4MediumProcAgent(key,directives)

    @staticmethod
    def createHostAgent(akey, videothumb, directives):
        if akey == BVOneClickConf.YOUTUBE: return YoutubeMediaHostAgent(akey, videothumb, directives)
        if akey == BVOneClickConf.VIMEO: return VimeoMediaHostAgent(akey, videothumb, directives)
        if akey == BVOneClickConf.HWDAUDIO: return HWDAudioMediaHostAgent(akey, videothumb, directives)
        if akey == BVOneClickConf.HWDVIDEO: return HWDVideoMediaHostAgent(akey, videothumb, directives)
        if akey == BVOneClickConf.S3AUDIO: return S3AudioMediaHostAgent(akey, videothumb, directives)
        if akey == BVOneClickConf.S3VIDEO: return S3VideoMediaHostAgent(akey, videothumb, directives)

