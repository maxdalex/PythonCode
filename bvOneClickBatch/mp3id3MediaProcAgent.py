import subprocess
import os.path
import eyed3
import eyed3.id3
from eyed3 import *
import base64
import time

from bvOneClickCT import *
from bvOneClickMD import *
from bvOneClickUtils import BVOneClickMessageLog

#### module confuguration ########
_log = BVOneClickMessageLog('mp3id3AudioProc')

# this is the BV logo 600x600 coded in b64
bvlogob64 = "ABHZ34+j8dcfH4sf0rs25YO/b3lZVrw7GZcUsedU9S1SfJPhzOvJ21tSsRPWHLjarVvaZjuudebLn7ntlhYEPFysa/G7GFVHhQ=="
bitrate = '128k'


###  MAPPING of Talk Info into ID3 ###
"""
    ########  Recognized by Windows and Itunes  ########################
    LOGO .jpg --> front cover
    TalkDescriptor.EDITOR : ---> Publisher (only windows)
    TalkDescriptor.DATE : --> Year + Encoded in Comment + encoded in title
    ## WARNING DATE: the date of the talk should be in a date field to make searches --> Windows file modified date
    # Artist is set with a suffix '- Balanced View' to make clear in Itunes the trainer is not a singer ;-)
    TalkDescriptor.TRAINER : --> artist ( with "Balanced View" suffix)
    'Balanced View' --> Album Artist
    TalkDescriptor.CONTEXT : --> album + encoded in subtitle
    TalkDescriptor.TITLE : --> title

    ######### The following info is not recognize by Windows an dItuens so it goes encoded in the comment field
    TalkDescriptor.LANGUAGE : --> Encoded in Comment
    TalkDescriptor.DESC : --> Encoded in Comment
    TalkDescriptor.TAGS : --> Encoded in comment
    TalkDescriptor.CATEGORY : --> Encoded in comment
    TalkDescriptor.ACCESS : --> encoded in comment
    TALK ID: -----------------> encoded in comment
    ExcerptCompilationOf------> encoded in comment

    ###THis info is not mapped
    TalkDescriptor.FNAME : --> None
    TalkDescriptor.SEODESC : NONE
    TalkDescriptor.SEOTAGS : NONE
"""

class ID3Map (object):
    def getComment(self):
        date = '_Date: '+ self.getDate()
        tags = '_Tags: '+ ''.join(self.__talk.getTopicTags())
        category = '_Category: '+ self.__talk.getCategory()
        description =  '_Description: '+ self.__talk.getQuote()
        access =  '_Access: '+ self.__talk.getAccess()
        language =  '_Language: '+ self.__talk.getLanguage()
        excerpt = '_ExcerptCompOf: '+ self.__talk.getExcerptOf()
        id = '_TalkID: ' + self.__talk.getID()

        comment = date + '\n' + tags + '\n' + category + '\n'  + description + '\n' + access + '\n'  + language + '\n'  + excerpt + '\n'+ id

        return  unicode(comment, "utf-8")

    def getAlbum(self):
        a = self.__talk.getContext()
        return unicode(a, "utf-8")

    def getAlbumArtist(self):
        return u"Balanced View"

    def getArtist(self):
        a = 'Balanced View ' +  self.__talk.getTrainer()
        return unicode(a, "utf-8")

    def getTitle(self):
        a =  self.getDate() + ' '+ self.__talk.getTrainer() + ':' + self.__talk.getTitle()
        return unicode(a, "utf-8")

    def getSubtitle(self):
        a = self.__talk.getContext()
        return unicode(a, "utf-8")

    def getPublisher(self):
        a = self.__talk.getEditor()
        return unicode(a, "utf-8")

    def getFrontCover(self):
        'return the image in binary'
        image = base64.b64decode(bvlogob64)
        return image
        """
        example taken form stackoverflow:
        import base64
        >>> encoded = base64.b64encode('data to be encoded')
        >>> encoded
        'ZGF0YSB0byBiZSBlbmNvZGVk'
        >>> data = base64.b64decode(encoded)
        >>> data
        'data to be encoded'
        Using this ability you can base64 encode an image and embed the resulting string in your program. To get the original image data you would pass that string to base64.b64decode.
        :return:
        """
    def getYear(self):
        date = self.__talk.getDate()
        year = time.strftime("%Y", date )
        return unicode(year, "utf-8")
    def getDate(self):
        date = self.__talk.getDate()
        s = time.strftime("%d/%m/%y", date)
        return s

    def __init__(self,talk):
        self.__talk = talk



class MP3ID3SMediumProcAgent (BVMediumProcAgent):

    def __extractAudioFromVideo(self,video, fname):
        # return an a media source of type audio

        #the audio is extracted into the same dir as the video
        audiodir = os.path.dirname(video.url)
        audiopath = os.path.join(audiodir,fname)

        #Extraction happens at 128Kbs and join the stero in one mono
        # Note that ffmpeg accepts multiple input files each containing one of more streams of different types
        # with more of one stream of the same type also possible (video/audio/subtitle/attachment/data)..
        # a names the audio stream.
        # muxing/demuxing: a file video contains many files inside. Demuxing explode it in its components, muxing does
        # the opposite
        #
        # -i filename = input file
        # -b:a 128 = apply bitrate parameter to the :a stream of the input with value 128k
        # -ac:a 1 = for the output only use one channel (1) of the input audio stream (:a)
        # -y = the output file is overwirtten without asking
        #- v 24: verbose on only the warnings
        # -ss 4: starts extracting from the 5th second of the input
        cmd = 'ffmpeg -ss 4 -v 24 -i ' + video.url + ' -b:a '+ bitrate+ ' -ac:a 1 -y ' + audiopath
        _log.stdout(cmd)
        res = subprocess.call(cmd)

        # raise an exception if something went wrong

        # trim the extracted audio 4 seconds both sides
        # see http://stackoverflow.com/questions/43890/crop-mp3-to-first-30-seconds
        # TRIMMING IS MORE COMPLICATED THAN I EXPECTED; check SOX
        #cmd = "ffmpeg -y -t 30 -i " + audiopath + "-acodec copy "
        #_log.stderr('WARNING:  Trimming audio is not yet implemented')

        return BVMediaSource(audiopath, BVMediaTypes.AUDIO)



    def __applyID3TAgs(self, talk, afile):

        _log.stdout('Applying  Id3tags to ' + afile)
        map = ID3Map(talk)

        # Old version with API
        #need to specify the ID3 version
        audiofile = eyed3.load(afile, eyed3.id3.ID3_V2_3 )

        # set windows-Itunes tags
        audiofile.tag.artist = map.getArtist()
        audiofile.tag.album =  map.getAlbum()
        audiofile.tag.album_artist = map.getAlbumArtist()
        audiofile.tag.title = map.getTitle()
        audiofile.tag.comments.set(map.getComment())
        audiofile.tag.publisher = map.getPublisher()
        audiofile.tag.year = map.getYear()
        audiofile.tag.subtitle = map.getSubtitle()

        # DATE PROBLEM UNRESOLVED
        # set last modified date in the file to the date of the talk to be used in queries
        # Modified date never changes for a read only file. Not sure about download though.
        #COnsider that in Windows the field year accept any number so even ddmmyy could be used.
        # THE BV HTTP SERVER DOES NOT TRANSMIT THE TIME STAMP
        #time = talk.getDescriptor()[TalkKeys.Descriptor.DATE]
        #os.utime(audio.url, (time, time))
        _log.stderr('WARNING: file mod date: time needs to be converted in number. Modified date not set')
        _log.stderr('WARNING: file mod date is not trasnmitted by the BV http server. Please fix')

        # Set Cover Image (code =3)
        imagedata = map.getFrontCover()
        #imagedata = open("BVlogo.jpg","rb").read()
        audiofile.tag.images.set(3, imagedata,"image/jpeg",u"Balanced View")

        # write it back
        audiofile.tag.save(None, eyed3.id3.ID3_V2_3)

        """ Version with command line. Command LIne is not an executable and  requires Python :-(

         # set windows-Itunes tags
        artist = map.getArtist()
        album =  map.getAlbum()
        album_artist = map.getAlbumArtist()
        title = map.getTitle()
        comments = map.getComment()
        publisher = map.getPublisher()
        _log.stderr('WARNNG: YEAR and SUBTITLE not implemented yet')
        #map.getYear()
        #map.getSubtitle()

        # DATE PROBLEM UNRESOLVED
        # set last modified date in the file to the date of the talk to be used in queries
        # Modified date never changes for a read only file. Not sure about download though.

        #COnsider that in Windows the field year accept any number so even ddmmyy could be used.
        # THE BV HTTP SERVER DOES NOT TRANSMIT THE TIME STAMP
        #time = talk.getDescriptor()[TalkKeys.Descriptor.DATE]
        #os.utime(audio.url, (time, time))
        _log.stderr('WARNING:time needs to be converted in number. Modified date not set')
        _log.stderr('WARNING: file date is not trasnmitted by the BV http server. Please fix')

        # Set Image
        coverfpath = map.getCover()

        # put the eyed3 command together
        # find the way to call the module without the OS !
        command = "eyed3 --artist %s --album %s --album-artist %s --title %s --comment %s --publisher %s" % (artist, album, album_artist, title, comments, publisher, coverfpath )
    """

    def processMedium(self):
        'rememebr that if the process is not required it is not called'

        talk = self.getmedium().getTalk()
        handle = self.getmedium().getSource().url
        _log.stdout('extract and tag audio for '+ talk.getID())

        #find the video source
        media = talk.getMedia()
        video = None
        for m in media:
            if m.getType() == BVMediaTypes.VIDEO: video = m.getSource()

        #create the filepath
        fpath = talk.getFileNamePrefix()+'.mp3'

        audio = self.__extractAudioFromVideo(video, fpath)

        if audio!= None:
            self._dispatchSuccess(audio,'')

        # apply TAgs to the audio file
        self.__applyID3TAgs(talk,audio.url)

        return

    def __init__(self, key, ds):
        super(MP3ID3SMediumProcAgent, self).__init__(key, ds)