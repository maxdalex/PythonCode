from bvOneClickConfig import *


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
    'An agent managing the hosting of a particular medium of a talk on a certain platform. It is a concrete class with abstract methods'

    #recognized directives
    PRIMARYHOST = '_primary'
    UPLOAD = '_upload'
    REMOTELNK = '_remotelnk'
    VIDEOTHUMB = '_videothumb'
    TRAINTHUMB = '_trainthumb'

    # ABSTRACT METHODS: actions of the agent to be implemented in the subclasses
    # provided in the configuratin of the framework
    def upload(self): pass

    def _initSubclass(self,key, thumb, ds ): pass
    'this is the initializer of the subclass called at the end of the constructor'
    # This avoid for the subclass to need to call the constructor of the superclass in tis own constructor if needed
    # end ABSTRACT METHODS

    #provides a success/failure event
    def subscribe(self,hostAgentEventHandler):
        self._eventHandlers.append(hostAgentEventHandler)

    # event dispatching private methods
    def _dispatchSuccess(self, handle, msg ):
        for h in self._eventHandlers: h.handleSuccess(self, handle, msg)

    def _dispatchFailure(self, msg):
        for h in self._eventHandlers: h.handleFailure(self, msg)

    # key is used to identify the agent
    def getID(self): return self.__key

    def setMedia(self, media) : self.__media = media
    def getMedia(self): return self.__media

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

        #complete with subclass initiliazation
        self._initSubclass(key, thumb, ds)


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
           self._statedict[agentkey]= code

    def updateItem(self, agentkey, value):
        self._statedict[agentkey]= value

    def getItems(self):
        'return a list of the items'
        return (self._statedict).items()

    def __init__(self):
        self._statedict = {}

class OcuTalkDescriptor (object):
    ' This class is useful to compact the talk basic fields in one object dictionary'

    LISTDELIMITER =','

    ID = 'id'
    EDITOR = 'editor'
    DATE = 'date'
    TRAINER = 'trainer'
    CONTEXT = 'context'
    LANGUAGE = 'language'
    QUOTE = 'quote'
    #SEODESC = 'seodesc'
    TAGS = 'tags'
    #SEOTAGS = 'seotags'
    CATEGORY = 'category'
    ACCESS = 'access'
    #FNAME = 'filename' #deprecated
    TITLE = 'title'
    EXCPTCOMP = 'excerptcompof' #excpert of or compilation of

    def __init__(self):
        self.__descdict = {}

    def getValue(self, key):
        res = self.__descdict[key]
        return res
    def setValue(self,key, value):
        self.__descdict[key]=value

    def setValueAsString(self, key, svalue):
        'it accepts a string value and convert it in the appropriate type within the descriptor'
        #date format = dd/mm/yyyy;

        if key == OcuTalkDescriptor.TAGS:
            tlist = svalue.split(LISTDELIMITER)
            self.__descdict[key]=tlist

        elif key == OcuTalkDescriptor.DATE:
            date = time.strptime(svalue, "%d/%m/%y")
            self.__descdict[key]=date

        else: self.setValue(key,svalue)

    def importFromStringDict(self, stringDict):
       'it set all values of the given string dictionary converting them in the appropriate type in the descriptor'
       for item in stringDict:
            key = item[0]
            value = item[1]
            self.setValueAsString(key, value)

class OcuJobAgentsPattern (object):
    'The  pattern decides what/how/where media of a talk are given a process or hosting agent'

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
            if (agentkey != BVMediumProcAgent.VIDEOSOURCE) and (agentkey != BVMediumProcAgent.AUDIOSOURCE):
                if self.isActive(agentkey):
                  res.append(agentkey)
        return res

    def getHostAudioAgentsKeys(self):
        res = []
        for item in self.__apattern:
            agentkey = item[0]
            if (agentkey != BVMediumProcAgent.VIDEOSOURCE) and (agentkey != BVMediumProcAgent.AUDIOSOURCE):
                if self.isActive(agentkey): res.append(agentkey)

        return res

    def __init__(self, agentsptn):
        """
        Example of pattern :
         pattern = {
                AUDIO: {
                    AUDIOSRC: "%s" % (BVMediumProcAgent.EXTRACTAUDIO),
                    HWDAUDIO: "%s,%s" % (UPLOAD, PRIMARYHOST),
                    S3AUDIO: ''
                },
                VIDEO: {
                    VIDEOSRC:'',
                    YOUTUBE: "%s,%s" % (UPLOAD, PRIMARYHOST),
                    VIMEO: '',
                    HWDVIDEO: "%s,%s" % (UPLOAD, REMOTELNK),
                    S3VIDEO: ''
                }
         }
        """
        self.__apattern = agentsptn[BVMediaTypes.AUDIO]
        self.__vpattern = agentsptn[BVMediaTypes.VIDEO]


class OcuTalkJobFactory (object):
    'it provides methods to create a talk job with its composite structure'

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

    #immutable ID
    def getID(self): pass

    # basic fields
    def getEditor(self): pass
    def getDate(self):pass
    def getTrainer(self):pass
    def getContext(self):pass
    def getLanguage(self):pass
    def getQuote(self):pass
    def getTopicTags(self):pass
    def getCategory(self):pass
    def getAccess(self):pass
    def getTitle(self):pass
    def getExcerptOf(self):pass

    # derived calculated fields
    def getSEOTags(self):pass
    def getSEODesc(self):pass
    def getVideoTitle(self):pass
    def getAudioTitle(self):pass
    def getFileNamePrefix(self):pass

    # media and agents
    def addMedium(self, medium):pass
    def getMedia(self): pass
    def getAllAgents(self):pass
    def subscribeAgentsHandler(self, ocuAgentEventHndl):pass
    'this will subscribe the handler to all agents of the talk'





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


    def getID(self): return self.__ID

     # basic fields
    def getEditor(self):    return self.__descriptor[OcuTalkDescriptor.EDITOR]
    def getDate(self):      return self.__descriptor[OcuTalkDescriptor.DATE]
    def getTrainer(self):   return self.__descriptor[OcuTalkDescriptor.TRAINER]
    def getContext(self):   return self.__descriptor[OcuTalkDescriptor.CONTEXT]
    def getLanguage(self):  return self.__descriptor[OcuTalkDescriptor.LANGUAGE]
    def getQuote(self):     return self.__descriptor[OcuTalkDescriptor.QUOTE]
    def getTopicTags(self): return self.__descriptor[OcuTalkDescriptor.TAGS]
    def getCategory(self):  return self.__descriptor[OcuTalkDescriptor.CATEGORY]
    def getAccess(self):    return self.__descriptor[OcuTalkDescriptor.ACCESS]
    def getTitle(self):     return self.__descriptor[OcuTalkDescriptor.TITLE]
    def getExcerptOf(self): return self.__descriptor[OcuTalkDescriptor.EXCPTCOMP]

    # derived calculated fields
    def getSEOTags(self):pass
    def getSEODesc(self):pass
    def getVideoTitle(self):    return "%s_Vtitle"%(self.getID())#mockup
    def getAudioTitle(self):    return "%s_Atitle"%(self.getID())#mockup
    def getFileNamePrefix(self):return "%s_Fname"%(self.getID())#mockup

    def getBasicDescriptor(self): return self.__descriptor

    def addMedium(self, medium):
        medium.setTalk(self)
        self.__medialist.append(medium)

    def getMedia(self): return self.__medialist

    def getAllAgents(self):
        'return a list with all proc and host agents configured in the talk'
        agents = []
        medialist = self.getMedia()
        for m in medialist:
            agents.extend(m.getAllAgents())

        return agents

    def subscribeAgentsHandler(self, ocuAgentEventHndl):
        'subscribe the agent handler to all agents of the talk'
        agents = self.getAllAgents()
        for a in agents:
            a.subscribe(ocuAgentEventHndl)
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
        self.__ID = descriptor[OcuTalkDescriptor.ID]
        self.__descriptor = descriptor
        self.__action = action
        self._status = status
        self._statusHandler = BVTalkJob._UpdateStatusHandler(status)
        self.__medialist = []

########################### end of class Talk ############################










