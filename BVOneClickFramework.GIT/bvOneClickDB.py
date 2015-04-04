

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


class BVOneClickDB (object):
    'singletone representing the DB module'

    #ABSTRACT METHODS
    def openDB(self): pass
    def getTalkJobs(self): pass



class TalkKeys (object):
    'provides constant standardized keys for all relevants elements of a talk '
    ID = 'id'
    STATUS = 'status'
    ACTION = 'action'

    class BVMediaTypes:
        VIDEO = 'video'
        AUDIO = 'audio'
        THUMB = 'thumb'

    class Descriptor (object):
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
        EXCPTCOMP = 'excerptcompof'
        #UPLDPATTERN =  'pattern' # storage may not be needed as implicit in the list of media host : it culd be HWD, youtube, vimeo


class TalkDescriptor (object):
    ' Due to the number of fields descriptor is implemtented as a dictionary to be safer and more extendible'

    def __init__(self, d):
        self.__descdict = d

    def getValue(self, key):
        res = self.__descdict[key]
        return res


class MediaThumbnail (object):
    'thumbnails are associated to a media host.'
    def __init__(self, url):
        self.__url = url


class MediaSource (object):
    def toString(self): return self.url
    def __init__(self, srcurl, t, directives = None):
        'the attribute  params is a host dependent info carried along in the framework'
        self.type = t
        self.url = srcurl
        self.directives = directives

class BVMediaProcEventHandler (object):
    'abstract class defining an handler'
    def processSuccess(self, agent, handle,msg):pass
    def processFailure(selfself, agent, msg):pass


########################## WARNING: this needs a similar thing as a Src Process Agent ###########################
# Let us use the same pattern used for host agent with source agents. Every media will be encapuslated in a
# media agent. IN this agent we can have a event submission that works like in the host agents.
# We can even have a superclass agent for that with just one event handler type.

class BVMediaProcAgent (object):
    ' it is the processor of a specific media'

    # directives recognized
    EXTRACTAUDIO = "_extract_"

    def __init__(self,key, ds):
        'ds should be a list'
        self._media = None
        self._eventHandlers = []
        self._directives =ds
        self._key = key

    # it sends event like the agents.
    def subscribe(self, mediaProcEventHandler):
        self._eventHandlers.append(mediaProcEventHandler)
    def _dispatchSuccess(self, handle, msg):
        for h in self._eventHandlers: h.processSuccess(self, handle, msg)
    def _dispatchFailure(self, msg):
        for h in self._eventHandlers: h.processFailure(self, msg)


    def setmedia (self, media): self._media = media
    def getmedia (self): return self._media
    def processMedia(self): pass
    def getkey(self): return self._key





class BVTalkMedia (object):
    'A media has a media source and a list of hosts. If empty = is not hosted'
    def isHosted(self): pass
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

        # set my talk as the talk of the host
        #talk = self.getTalk()
        #host.setTalk(talk)

        #set myself as the media of the host
        host.setMedia(self)

        #register the status handler
        handler = self.getTalk().getStatusHandler()
        host.subscribe(handler)




    def appendHostAgent(self, host):
        #ASSERT: when a host is added the media needs to be already associated to a talk

        self.__ohosts.append(host)

        # set myself as the media of the host
        host.setMedia(self)

        #register the status handler
        handler = self.getTalk().getStatusHandler()
        host.subscribe(handler)

    def setProcessAgent(self, pagent):
        #ASSERT: when a agent  is added the media needs to be already associated to a talk
        talk = self.getTalk()
        self._pagent = pagent

        #register the status handler
        handler = talk.getStatusHandler()
        pagent.subscribe(handler)

    def getProcessAgent(self): return self._pagent

    def __init__(self,  msrc):

        self.__talk = None
        self.__msrc =  msrc
        self.__phost = None
        self._pagent = None
        self.__ohosts = []


# defined by subclasses
class TalkMediaHostHandle (object):
    def toString(self):pass

class BVMediaHostEventHandler (object):
    'Abstract Calss. we put an event handler straight into the agents.Keep it simple '
    def uploadSuccess(self, agent, mediaHostHandle, msg ):pass
    def uploadFailure(self, agent, msg): pass

class BVMediaHostAgent (object):

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

    #event types
    UPLOAD_SUCCESS = 0
    UPLOAD_FAILURE = -1


    #def setTalk(self, t): __talk = t


    def subscribe(self,hostAgentEventHandler):
        self._eventHandlers.append(hostAgentEventHandler)

    def _dispatchSuccess(self, handle, msg ):
        for h in self._eventHandlers: h.uploadSuccess(self, handle, msg)

    def _dispatchFailure(self, msg):
        for h in self._eventHandlers: h.uploadFailure(self, msg)

    def upload(self): pass
    def download(self, dest): pass
    def getStatus(self): pass
    def modify(self, attribute, value): pass
    # key is used to identify the agent for I/O purpose
    def getkey(self): return self.__key

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
class BVTalk (object):
    """
    ######################## How the complex of a talk is created in the constructors #########################

    1. A talk is created without media and hosts. Media are added with AddMEdia. AddMedia calls the setTalk in media.
    2. A media is created on its own out of a talk and without media hosts.
    2A. A media process agent is created from the media
    2B. Before hosts are added the media (process agent) needs to be associated to a talk.
    3. Media hosts are added  with appendHost appendHost calls the setMedia in host
    3. A media host is created on its own and later added to a media with append host.
    """

    """
    __eventHandlers = []

    # SUBSCRIBE EVENTS: to keep it simple for the moment rather than a subscribe pattern we only register a callback from the only listener
    # printing messages is instead made by calling static methods of the class UI
    def subscribe(self, handler):
        self.__eventHandlers.append(handler)

    def dispatchEvent(self, event):
        for h in self.__eventHandlers:
            h.handle(event)

    """


    def subscribeToAllAgents(self, handler):
        'subscribe the handler to all agents involved in the talk'
        agents = self.getAllAgents()
        for a in agents:
            a.subscribe(handler)

    def addMedia(self, media):
        media.setTalk(self)
        self.__medialist.append(media)



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

    # reset status goes trhough all media hosts, check them and update global status. Events are sent.
    #def resetStatus(self):pass


#class BVTalkJob (object):
    'represent a job to be done on a talk'
    NOOP = 'NOOP'
    SKIP = 'SKIP'
    UPLOAD = 'UPLOAD' # in case something went wrong it completes that part of uploads
    REPLACE_VIDEO = 'replacevideo'
    REPLACE_AUDIO = 'replaceaudio'
    MODIFY_DESC = 'modifydesc'

    class UpdateStatusHandler(BVMediaHostEventHandler, BVMediaProcEventHandler):
        ' it is subscribed in all agents and update the state of the job when agents report their results'

        def processSuccess(self, agent, handle, msg):
            key = agent.getkey()
            self._status.updateItem(key, BVJobStatus.DONE)


        def processFailure(self, agent, msg):
             key = agent.getkey()
             self._status.updateItem(key, BVJobStatus.NOTDONE)


        def uploadSuccess(self, agent, handle, msg ):
            key = agent.getkey()
            self._status.updateItem(key, BVJobStatus.DONE)


        def uploadFailure(self, agent, msg):
           key = agent.getkey()
           self._status.updateItem(key, BVJobStatus.NOTDONE)


        def __init__(self, status):
            self._status = status

    ################################# end of class UpdateStatus Handler ###########################################

    """
    def _subscribeStatusHandler(self, talk, handler):
        'it subscribe the handler to all agents'
        agents = talk.getAllAgents()
        for a in agents:
            a.subscribe(handler)
    """

    def getStatusHandler(self):
        return self._statusHandler
    #def getTalk(self): return self.__talk
    def getAction(self): return self.__action
    def getStatus(self): return self._status


    def __init__(self, id, descriptor, action, status):
        self.__ID = id
        self.__descriptor = descriptor
        self.__action = action
        self._status = status
        self._statusHandler = BVTalk.UpdateStatusHandler(status)
        self.__medialist = []
"""
        # subscribe the status handler
        handler = self.UpdateStatusHandler(status)
        self._subscribeStatusHandler(talk, handler)
"""

"""
 def __init__(self, id, d):
        #
        self.__ID = id
        self.__descriptor = d
        self.__medialist = []
"""

########################### end of class Talk ############################
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


########################################## MAIN TALK CLASS ###########################################################
class BVTalkEventType (object):
    NOTYPE = 0
    FAILURE = -1
    NEWMEDIAUPLOADED = 2



class BVTalkEvent (object):
    def __init__(self, talk, agent, type, message):
        self.talk = talk
        self.agent = agent
        self.type = type
        self.message = message


class BVTalkEventHandler (object):
    'an abstract class for specific handlers to be subscribed'
    def handle(self, event):pass







