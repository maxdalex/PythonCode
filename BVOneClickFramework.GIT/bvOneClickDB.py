from bvOneClickConfig import *

"""
 This module provides the model layer of MVC. It defines data types and raised events" \
" Many of the classes are abstract classes needed to be refined by the implementation details of real DB used" \
" in the first version the DB is implemented with google spread" \

Model:
 - a talk has several media
 - each media has a media proc agent which process the source file
 - each media can have one or more media hosts
 - one of the media hosts of a media is considered the primary media and is where is relied upon for retrieval
 - in the UI there is a column for each media host and media proc and a handler is registered on the media host and proc

NOTE: Every media host will use a specific handle to manage the hosted talk. Where are these hndles stored?
Best is that specific instance variables represnts instances of hosts within the talk rather than having
singletones around. REfine this idea. The Tak HOstingCOntrol needs to be an instance variable to store
the implementation dependent handlers for that particular talk.

Also different talks can have a different set of hosts, like be only on outube or only on viemo. So it is good
to have the HostControlObject passed to the constructor!

23/1/15
I realize I took an extreme approach wanting to see all action made on a talk as a method of the Talk class. It is better
to use a more balanced approach were some of the processing is made in separate classes on a Talk instance, This allow to
define a concrete Talk class in the BVOneClickFramework



"""


class OcuTalkJobManager (object):
    'interface representing a platform to manage talk jobs'
    def openDB(self): pass
    def getTalkJobs(self): pass


class TalkJobKeys (object):
    'provides constant standardized keys for all relevant elements of a talkjob '
    #ID = 'id'
    STATUS = 'status'
    ACTION = 'action'

class BVMediaTypes:
        VIDEO = 'video'
        AUDIO = 'audio'

class TalkDescriptorKeys (object):
        ID = 'id'
        EDITOR = 'editor'
        DATE = 'date'
        TRAINER = 'trainer'
        CONTEXT = 'context'
        LANGUAGE = 'language'
        DESC = 'description'
        SEODESC = 'seodesc'
        TAGS = 'tags'
        SEOTAGS = 'seotags'
        CATEGORY = 'category'
        ACCESS = 'access'
        FNAME = 'filename'
        TITLE = 'title'
        EXCPTCOMP = 'excerptcompof' #excpert of or compilation of



class TalkDescriptor (object):
    ' Due to the number of fields descriptor is implemtented as a dictionary to be safer and more extendible'

    def __init__(self, d):
        self.__descdict = d

    def getValue(self, key):
        res = self.__descdict[key]
        return res


class BVMediaSource (object):
    def toString(self): return self.url
    def __init__(self, srcurl, t, directives = None):
        'the attribute  params is a host dependent info carried along in the framework'
        self.type = t
        self.url = srcurl
        self.directives = directives


class BVAgentInterface (object):
    def getId(self):pass
    def subscribe(self, agenteventhandler): pass


class BVAgentEventHandlerInterface (object):
    'an interface defining a handler to deal with success/failure events'
    def handleSuccess(self, agent, mediaHostHandle, msg ):pass
    def handleFailure(self, agent, msg): pass

class BVMediumProcAgent (BVAgentInterface):
    ' it is the processor of a specific media'

    # directives recognized
    AUDIOSOURCE = 'audiosource'
    VIDEOSOURCE = 'videosource'
    EXTRACTAUDIO = '_extract_'

    def __init__(self,key, ds):
        'ds should be a list'
        self._media = None
        self._eventHandlers = []
        self._directives =ds
        self._key = key

    # success/failure event .
    def subscribe(self, mediaProcEventHandler):
        self._eventHandlers.append(mediaProcEventHandler)
    def _dispatchSuccess(self, handle, msg):
        for h in self._eventHandlers: h.processSuccess(self, handle, msg)
    def _dispatchFailure(self, msg):
        for h in self._eventHandlers: h.processFailure(self, msg)


    def setmedium (self, media): self._media = media
    def getmedium (self): return self._media
    def processMedium(self): pass
    def getKey(self): return self._key


class BVTalkMedium (object):
    'A medium has a medium source and a list of hosts.'
    def getType(self) : return self.__msrc.type
    def getPrimaryHost(self): return self.__phost
    def getOtherHosts(self): return self.__ohosts
    def getAllAgents(self):
        #host agents
        agents =[self.getPrimaryHost()]
        agents.extend(self.getOtherHosts())
        #process agent
        pagent = self.getProcessAgent()
        if pagent!=None:
            agents.append(pagent)
        return agents

    def getTalk(self): return self.__talk
    def getSource(self): return self.__msrc

    def setTalk(self,t):
        self.__talk =t

    def setPrimaryHost(self, host):
        #ASSERT: when a host is added the media needs to be already associated to a talk

        self.__phost= host

        #set myself as the media of the host
        host.setMedia(self)

        #register the talk status handler on the  new host
        handler = self.getTalk().getStatusHandler()
        host.subscribe(handler)


    def appendHostAgent(self, host):
        #ASSERT: when a host is added the media needs to be already associated to a talk

        self.__ohosts.append(host)

        # set myself as the media of the host
        host.setMedia(self)

        #register the talk status handler on the new host
        handler = self.getTalk().getStatusHandler()
        host.subscribe(handler)

    def setProcessAgent(self, pagent):
        #ASSERT: when a agent  is added the media needs to be already associated to a talk
        talk = self.getTalk()
        self.__pagent = pagent

        #also sets itself as the medium of the process agent
        pagent.setmedium(self)

        #register the talk status handler n the new host
        handler = talk.getStatusHandler()
        pagent.subscribe(handler)

    def getProcessAgent(self): return self.__pagent

    def __init__(self,  msrc):
        self.__talk = None
        self.__msrc =  msrc
        self.__phost = None
        self.__pagent = None
        self.__ohosts = []





class BVMediaHostAgent (BVAgentInterface):

    """
    It is one of the  hosts of a media for a talk. It also includes the thumb for that media on this host
    A Media host only hosts one media. Even if the platform is the same, different media hosts instances
    are used for different media.

    A media host is created without any association to a talk and then instantiated with a talk
    """
    #recognized directives
    PRIMARYHOST = '_primary'
    UPLOAD = '_upload'
    REMOTELNK = '_remotelnk'
    VIDEOTHUMB = '_videothumb'
    TRAINTHUMB = '_trainthumb'

    #provides a success/failure event
    def subscribe(self,hostAgentEventHandler):
        self._eventHandlers.append(hostAgentEventHandler)

    def _dispatchSuccess(self, handle, msg ):
        for h in self._eventHandlers: h.handleSuccess(self, handle, msg)

    def _dispatchFailure(self, msg):
        for h in self._eventHandlers: h.handleFailure(self, msg)

    # key is used to identify the agent
    def getID(self): return self.__key
    def upload(self): pass
    def download(self, dest): pass
    def getStatus(self): pass
    def modify(self, attribute, value): pass

    def setHandle(self, handle): self._handle = handle
    def getHandle(self): return self.__handle
    def setMedia(self, media) : self.__media = media
    def getMedia(self): return self.__media
    def getThumb(self): return self.__thumb
    def getTalk(self): return self.getMedia().getTalk()
    def getDirectives(self): return self.__directives#list


    def __init__(self, key, thumb, ds):
        # I expect ds to be a list
        self.__media = None
        self.__thumb = thumb
        self.__handle = None
        self.__directives = ds
        self.__key = key
        self._eventHandlers = []



##################### TALK vs TALKJOB #####################
# On 3rd of March 2015 I finally decide to give up the difference between talk and talk job. We only have talkjobs as the
# configuration of agents is actually part of the job configuration. Keeping them seprate only complicates

class BVJobInterface (object):
    'abstract class representing a job to be done on a talk'
    NOOP = 'NOOP'
    SKIP = 'SKIP'
    UPLOAD = 'UPLOAD'
    REPLACE_VIDEO = 'replacevideo'
    REPLACE_AUDIO = 'replaceaudio'
    MODIFY_DESC = 'modifydesc'

    def getStatusHandler(self):pass
    def getAction(self): pass
    def getStatus(self): pass

class BVTalkInterface (object):
    'abstract class representing a BV talk'
    def getID(self): pass
    def getDescriptor(self): pass
    def addMedium(self, medium):pass
    def getMedia(self): pass
    def getAllAgents(self):pass
    def subscribeAgentsHandler(self, ocuAgentEventHndl):pass
    'this will subscribe the handler to all agents of the talk'




class BVJobStatus (object):
    'it contains a dictionary in which all the main agents of the job are listed with a value done/not done'
    # Status only contains entries for the agents that are activated in a configuration.
    # It is set dyamically when agents are called, not statically.
    NOTDONE = "failure"
    DONE = "ok"



    # We pass the key rather than the agent because in some cases these methods are called before the agent is created
    # at loading time. Status is an entity in itself carrying information on the dynamic configuration of agents
    def isDone(self, agentkey):
        dict = self._statedict
        return (dict.has_key(agentkey)) and (dict[agentkey] == BVJobStatus.DONE)

    def addItem(self, agentkey, code = "failure"):
        # sorry. I put the string because syntax errors
           self._statedict[agentkey]= code

    def updateItem(self, agentkey, value):
        self._statedict[agentkey]= value

    def getItems(self):
        'return a list of the items'
        return (self._statedict).items()

    def __init__(self):
        self._statedict = {}

class OcuUploadPattern (object):
    'it models a particular pattern of upload for a talk'
    def isActive(self, agentKey):
        directives = self.getDirectives(agentKey)
        return (directives != '')

    def isPrimary(self, agentKey):
        id = agentKey.getKey()
        list = (self.getDirectives(agentKey)).split(',')
        res =  BVMediaHostAgent.PRIMARYHOST in list
        return res

    def getDirectives(self, agentKey):
        if agentKey in self.__apattern: return self.__apattern[agentKey]
        else : return self.__vpattern[agentKey]

    def getHostVideoAgentsKeys(self):
        res = []
        for item in self.__vpattern :
            agentkey = item[0]
            if (agentkey != BVMediumProcAgent.VIDEOSOURCE) and (agentkey != BVMediumProcAgent.AUDIOSOURCE)\
                    and self.isActive(agentkey):
                res.append(agentkey)
         return res

    def getHostAudioAgentsKeys(self):
        res = []
        for item in self.__apattern:
            agentkey = item[0]
            if (agentkey != BVMediumProcAgent.VIDEOSOURCE) and (agentkey != BVMediumProcAgent.AUDIOSOURCE):
                if self.isActive(agentkey): res.append(agentkey)

         return res

    def __init__(self, audiopattern, videopattern):
        """
        Example of pattern dicitonaries:
        audiopattern = {
            AUDIOSRC: "%s" % (BVMediaProcAgent.EXTRACTAUDIO),
            HWDAUDIO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            S3AUDIO: ''
        }

        videopattern = {
            VIDEOSRC:'',
            YOUTUBE: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            VIMEO: '',
            HWDVIDEO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.REMOTELNK),
            S3VIDEO: ''
        }
        """
        self.__apattern = audiopattern
        self.__vpattern = videopattern



class OcuTalkJobFactory (object):
    'it provides methods to create a talk job with its composite structure'


    @staticmethod
    def __valueToAction(v): return v
    @staticmethod
    def __valueToURL(v): return v
    @staticmethod
    def __valueToDate(v):
        date =time.strptime(v, "%d/%m/%y")
        return date
    @staticmethod
    def __valueToTagList(v): return v.split(UIdirectives.LISTDELIMITER)

    @staticmethod
    def createTalkDescriptor(stringDict):pass
    'given a dictionary of strings it creates another dictionary with the right types (lists, dates, etc)'

    @staticmethod
    def createTalkJob(action, status,  talkdesc, videosrc, videothumb, uploadptrn, audiosrc=None):
        'Given the basic input it creates the whole structure of a talk job'
        """
        all considered as a URL. fileds in talkdesc nedd to have the right type.
        """

        #################### Talk creation #######################
        talkjob = BVTalkJob(talkdesc, action, status)

        ######################## Media and Process Media Creation #######################
        # video  medium
        video = BVMediaSource(videosrc, BVMediaTypes.VIDEO)
        videomedium = BVTalkMedium(video)

        #add the video medium to the talkjob
        talkjob.addMedium(videomedium)

        #set the process agent for the video medium if needed
        agentkey = BVMediumProcAgent.VIDEOSOURCE
        if uploadptrn.isActive(agentkey) and (not status.isDone(agentkey)):
            videoproc = BVOneClickConf.createVideoSrcProcAgent(agentkey, uploadptrn.getDirectives(agentkey))
            videomedium.setProcessAgent(videoproc)

        # audio medium
        audio = BVMediaSource(audiosrc, BVMediaTypes.AUDIO)
        audiomedium = BVTalkMedium(audio)

        #add the audio medium to the talkjob
        talkjob.addMedium(audiomedium)

        #set the process agent for the video medium if needed
        agentkey = BVMediumProcAgent.AUDIOSOURCE
        if uploadptrn.isActive(agentkey) and (not status.isDone(agentkey)):
            audioproc = BVOneClickConf.createAudioSrcProcAgent(agentkey, uploadptrn.getDirectives(agentkey))
            audiomedium.setProcessAgent(audioproc)

        ################  VIDEO Host Agents creation and setting in the medium ##########################

        # get the list of video active hosts fot the upload pattern
        hosts = uploadptrn.getHostVideoAgentKeys()
        for hagentkey in hosts:
            if not status.isDone(hagentkey):
                # creates the medium host
                host = BVOneClickConf.createHostAgent(hagentkey, videothumb, uploadptrn.getDirectives(hagentkey))
                # add the host to the video medium
                if uploadptrn.isPrimary(hagentkey):
                    videomedium.setPrimaryHost(host)
                else:
                    videomedium.appendHostAgent(host)

        ################  AUDIO Host Agents creation and setting in the medium ##########################

        # get the list of audio  active hosts fot the upload pattern
        hosts = uploadptrn.getHostAudioAgentKeys()
        for hagentkey in hosts:
            if not status.isDone(hagentkey):
                # creates the medium host
                host = BVOneClickConf.createHostAgent(hagentkey, videothumb, uploadptrn.getDirectives(hagentkey))
                # add the host to the audio medium
                if uploadptrn.isPrimary(hagentkey):
                    audiomedium.setPrimaryHost(host)
                else:
                    audiomedium.appendHostAgent(host)

        return talkjob


class BVTalkJob (BVJobInterface, BVTalkInterface):
    """
    ######################## How the complex of a talk is created in the constructors #########################

    1. A talk is created without media and hosts. Media are added with AddMEdia. AddMedia calls the setTalk in media.
    2. A medium is created on its own out of a talk and without media hosts.
    2A. A media process agent is created from the media
    2B. Before hosts are added the media (process agent) needs to be associated to a talk.
    3. Media hosts are added  with appendHost appendHost calls the setMedia in host
    3. A media host is created on its own and later added to a media with append host.
    """

    #######  BEGIN Talk Interface implementation ###########
    def subscribeAgentsHandler(self, ocuAgentEventHndl):
        'subscribe the agent handler to all agents of the talk'
        agents = self.getAllAgents()
        for a in agents:
            a.subscribe(ocuAgentEventHndl)

    def addMedium(self, medium):
        medium.setTalk(self)
        self.__medialist.append(medium)


    def getID(self): return self.__ID
    def getDescriptor(self): return self.__descriptor
    def getMedia(self): return self.__medialist
    def getAllAgents(self):
        'return a list with all proc and host agents configured in the talk'
        agents = []
        medialist = self.getMedia()
        for m in medialist:
            agents.extend(m.getAllAgents())

        return agents
    ################ END  Talk Interface Implementation ##################

    ################ BEGIN Job Interface Implementation ##################
    def getStatusHandler(self):
        return self._statusHandler

    def getAction(self): return self.__action
    def getStatus(self): return self._status
    ############### END Job Interface Implementation ##################

    # Agents handler of the Talk
    class _UpdateStatusHandler(BVAgentEventHandlerInterface):
        'Private class of the Talk : it is the event handler that keeps the job status updated after agents actions'

        def handleSuccess(self, agent, handle, msg):
            key = agent.getKey()
            self._status.updateItem(key, BVJobStatus.DONE)

        def handleFailure(self, agent, msg):
             key = agent.getKey()
             self._status.updateItem(key, BVJobStatus.NOTDONE)

        def __init__(self, status):
            self._status = status
    # end agent handler

    def __init__(self,  descriptor, action, status):
        self.__ID = descriptor[TalkDescriptorKeys.ID]
        self.__descriptor = descriptor
        self.__action = action
        self._status = status
        self._statusHandler = BVTalkJob._UpdateStatusHandler(status)
        self.__medialist = []

########################### end of class Talk ############################










