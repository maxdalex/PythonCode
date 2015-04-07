import gspread
from bvOneClickMD import *
from bvOneClickCT import *
from bvOneClickUI import *
from youtubeMediaHostAgent import *
from vimeoMediaHostAgent import *
from s3MediaHost import *
from hwdMediaHost import *
from mp3id3MediaProcAgent import *
from mp4MediaProcAgent import *


SPREADSHEET= '1dwjdmi77m9gVFts5WYawy_k11LekmB7ejjo-5VkU0QQ'
LISTDELIMITER =','

log = BVOneClickMessageLog('gspreadUIDB')

#THE worksheet handle to gdata. Global to the module
_WKS = None

# shortcuts to constant values for agent directives
EXTRACTAUDIO = BVMediumProcAgent.EXTRACTAUDIO
PRIMARYHOST = BVMediaHostAgent.PRIMARYHOST
UPLOAD = BVMediaHostAgent.UPLOAD
REMOTELNK = BVMediaHostAgent.REMOTELNK
VIDEOTHUMB = BVMediaHostAgent.VIDEOTHUMB
TRAINTHUMB = BVMediaHostAgent.TRAINTHUMB

#sheet columns names
YOUTUBE = BVOneClickConf.YOUTUBE
VIMEO = BVOneClickConf.VIMEO
HWDAUDIO = BVOneClickConf.HWDAUDIO
HWDVIDEO = BVOneClickConf.HWDVIDEO
S3AUDIO = BVOneClickConf.S3AUDIO
S3VIDEO = BVOneClickConf.S3VIDEO

VIDEOSRC = BVMediumProcAgent.VIDEOSOURCE
AUDIOSRC = BVMediumProcAgent.AUDIOSOURCE

ID = OcuTalkDescriptor.ID
ACTION =  TalkJobKeys.ACTION
STATUS = TalkJobKeys.STATUS
DATE = OcuTalkDescriptor.DATE
TRAINER = OcuTalkDescriptor.TRAINER
CONTEXT = OcuTalkDescriptor.CONTEXT
TITLE = OcuTalkDescriptor.TITLE
LANGUAGE = OcuTalkDescriptor.LANGUAGE
TAGS = OcuTalkDescriptor.TAGS
CATEGORY = OcuTalkDescriptor.CATEGORY
QUOTE = OcuTalkDescriptor.QUOTE
ACCESS = OcuTalkDescriptor.ACCESS
EDITOR = OcuTalkDescriptor.EDITOR
EXCPTCOMP = OcuTalkDescriptor.EXCPTCOMP


################## BV TALK EVENT HANDLER #######################
# This class is able to manage events launched by the talk and update the sheet accordingly
# Basically the host agents raise events in the talk and all subscribwers receive these events.
# In the message of the event the agent put its identificaton so the handler knows where to write.
# another possibility would be to include a UI handler with embedded coordinates in each single agent.
# I think only doing it through hte talk is a more general solution. A single handle may be able to amnage
# a globa; context of the interface

## KEEP IT SIMPLE: at the moment we only need host agent events to manage the result of uploads and other operation
# on the net. SO we operate with agent event nadlers.



############### Utilities ###############
# coding and deconding of status values
# status is represented in the UI/DB as a list of couples with semicolon
# ex: vimeo:ok, audio:failure, ...
def _statusToValue(status):
    string =None
    list = status.getItems()
    count =0
    for i in list:
        if count==0: string = "%s:%s" % (i[0], i[1])
        else: string = string + ",\n%s:%s" % (i[0], i[1])
        count = count+1


    return string


############################################### DB Section #####################################################




class UIMapper (object):
    'It manages the mapping between parameters and columns in the sheet picking by key rather than number'
    """
    In the sheet there is a mapping row (the first one) giving a fixed numeric code for each column. If new columns are added
    Or old ones are changed in position, the code remain the same and so the class methods are able to pick
    the right column number. We also have two mapings needed: col cod --> record field, col cod --> sheet column number
    Since we use get_all_records records are fetched as dictonary rather than a list. See below.
    """

    # DB keys are used  when available  UI specific KEY not provided by the DB layer are following
    UPLDPATTERN = 'upldpattern'

    # This dictionary translates column codes in column numbers. It is dynamically initialized within the UI
    cmap = {}

    # This dictionary translates the column codes into standard keys. This allows to change the labels of
    # the column in the sheet without affecting the program, which uses its own label system consistently
    map = {
            ID: '1',
            TalkJobKeys.ACTION: '2',
            TalkJobKeys.STATUS: '3',
            UPLDPATTERN: '4',
            DATE: '5',
            TRAINER: '6',
            CONTEXT: '7',
            TITLE: '8',
            LANGUAGE: '9',
            TAGS: '10',
            CATEGORY: '11',
            QUOTE: '12',
            ACCESS: '13',
            EDITOR: '14',
            VIDEOSRC: '15',
            AUDIOSRC: '16',
            VIDEOTHUMB: '17',
            TRAINTHUMB:'18',
            #OcuTalkDescriptor.FNAME: '19',
            #OcuTalkDescriptor.SEODESC: '20',
            #OcuTalkDescriptor.SEOTAGS: '21',
            YOUTUBE: '22',
            VIMEO:'23',
            HWDVIDEO : '24',
            HWDAUDIO:'25',
            S3VIDEO: '26',
            S3AUDIO:'27',
            EXCPTCOMP:'28'
        }


    ######################################################################
    # UPLOAD PATTERNS and STATUS are the foundation of the single job configuration
    #######################################################################
    # THe upload pattern decides what/how/where media are processed and hosted
    # It also define a State as a consequence in terms of which actions succeded and which did not
    # Initially the status is 'unprocessed'. Upon the first processing of the job, the status is set and
    # then kept updated.
    #

    # specific values for upload patterns as expcted in the sheet column "pattern upload"
    UPLD_YOUTUBE = 'youtube'
    UPLD_VIMEO = 'vimeo'
    UPLD_HWD = 'hwd'

    @staticmethod
    def isPrimary(dir):
        list = dir.split(',')
        res =  UIdirectives.PRIMARYHOST in list
        return res

    @staticmethod
    def isActive(selfdir):
        return (selfdir != '')


    #Dictionary of directives for the agents. Where the value is '' the agent is not activated
    updirectives = {

        UPLD_YOUTUBE: {
            VIDEOSRC:'',
            AUDIOSRC: "%s" % (BVMediumProcAgent.EXTRACTAUDIO),
            YOUTUBE: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            VIMEO: '',
            HWDAUDIO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            HWDVIDEO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.REMOTELNK),
            S3VIDEO: '',
            S3AUDIO: ''
        },
        UPLD_VIMEO: {
            VIDEOSRC:'',
            AUDIOSRC: "%s" % (BVMediumProcAgent.EXTRACTAUDIO),
            YOUTUBE: '',
            VIMEO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            HWDAUDIO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            HWDVIDEO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.REMOTELNK),
            S3VIDEO: '',
            S3AUDIO: ''
        },
        UPLD_HWD :{
            VIDEOSRC:'',
            AUDIOSRC: "%s" % (BVMediumProcAgent.EXTRACTAUDIO),
            YOUTUBE: '',
            VIMEO: '',
            HWDAUDIO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            HWDVIDEO: "%s,%s" % (UIdirectives.UPLOAD, UIdirectives.PRIMARYHOST),
            S3VIDEO: '',
            S3AUDIO: ''
        }
    }





class GSheetJobManager (OcuTalkJobManager) :
    #__talksJobs is inherited from the superclass
    #worksheet manager

    def __valueToStatus(self, v):
        s = BVJobStatus()

        # trim out all end of lines
        vv = v.replace("\n", "")

        # quick and dirty test for valid ststus
        if (':' in vv) :
            list = vv.split(',')
            for i in list:
                items = i.split(':')
                s.addItem(items[0], items[1])
        return s

    def __valueToAction(self,v): return v

    def __valueToURL(self,v): return v
    def __valueToDate(self,v):
        date =time.strptime(v, "%d/%m/%y")
        return date
    def __valueToTagList(self,v): return v.split(LISTDELIMITER)

    def __initColumnMapper(self):
        #read the first row
        value_list = _WKS.row_values(1)
        cnum = 1
        for v in value_list:
            UIMapper.cmap[v] =cnum
            cnum = cnum+1


    def __loadTalkDescriptor(self, desc, r):

        key = ID
        desc[key] = r[UIMapper.map[key]]

        key = DATE
        desc[key] = self.__valueToDate(r[UIMapper.map[key]])

        key = TRAINER
        desc[key] = r[UIMapper.map[key]]

        key = CONTEXT
        desc[key] = r[UIMapper.map[key]]

        key = EDITOR
        desc[key] = r[UIMapper.map[key]]

        key = LANGUAGE
        desc[key] = r[UIMapper.map[key]]

        key = QUOTE
        desc[key] = r[UIMapper.map[key]]

        key = TITLE
        desc[key] = r[UIMapper.map[key]]

        key = TAGS
        desc[key] = self.__valueToTagList(r[UIMapper.map[key]])

        key = CATEGORY
        desc[key] = r[UIMapper.map[key]]

        key = ACCESS
        desc[key] = r[UIMapper.map[key]]

        key = EXCPTCOMP
        desc[key] = r[UIMapper.map[key]]



    def __rowToTalk(self, r, rnum):
        'r is a row of the spreadsheet in form of a dictionary'

        # If the action is SKIP or NOOP it returns immediately
        action = self.__valueToAction(r[UIMapper.map[TalkJobKeys.ACTION]])
        if (action== BVTalkJob.SKIP or action == BVTalkJob.NOOP or action == '' ): return None

        desc = {}

        # create Status
        status = self.__valueToStatus(r[UIMapper.map[TalkJobKeys.STATUS]])

        # create descriptor
        self.__loadTalkDescriptor(desc, r)

        OcuTalkJobFactory.createTalkJob(action, status, talkdesc, videosrc, videothumb,uploadptrn,audiosrc)

        #################### Talk creation #######################
        talk = BVTalkJob(id, desc, action, status)

        #thumbs
        key = UIMapper.VIDEOTHUMB
        videothumb = self.__valueToURL(r[UIMapper.map[key]])

        #HWD Audio Thumbs for HWD
        key = UIMapper.TRAINTHUMB
        trainthumb = self.__valueToURL(r[UIMapper.map[key]])
        #log.stderr("HWD AudioThumbs loading not implemented yet!!!")


         # Upload Pattern. I decide not to code it in the sheet but rather here in the code
        # this to use the cells of the host agents in the sheet to report the result failures/success
        # Directives: this is a pattern of uploading encoded in UIdirectives
        # HostHandle: this is the id of the media hosted or an error message
        # An action agent is generated if: IS in directives AND does not have a handle yet.
        # IN case of failures of some of the agents, when theprogram is run again only the failed agents are considered
        key = UIMapper.UPLDPATTERN
        pattername = r[UIMapper.map[key]]
        upldpattern = UIMapper.updirectives[pattername]


        # The following code should go into the proc agent
        """
        if aurl == UIdirectives.EXTRACTAUDIO:
            audio = MediaSource("", TalkKeys.MediaTypes.AUDIO, [BVMediaProcAgent.EXTRACTAUDIO])
        else:
            aurl = self.__valueToURL(r[UIMapper.map[key]])
            audio = MediaSource(aurl, TalkKeys.MediaTypes.AUDIO)
        """

        ######################## media creations and setting of proc agents and talk #######################
        # Whenever a valid handle is available the process agents are not set

        # video  media
        key = UIMapper.VIDEOSRC
        # column code and column number are different
        # column number and column code are different: code is the key for the record field, num is the real col number
        ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        handle = self.__valueToURL(r[ccode])
        video = BVMediaSource(handle, TalkJobKeys.BVMediaTypes.VIDEO)
        videomedia = BVTalkMedium(video)

        talk.addMedium(videomedia)

        #vdirectives = (upldpattern[key]).split(UIdirectives.LISTDELIMITER)
        vdirectives = upldpattern[key]
        #invalidhandle = (handle == '') or (handle.find('ERROR'))

        if UIMapper.isActive(vdirectives) and (not status.isDone(key)):
            videoproc = MP4MediumProcAgent(key, vdirectives.split(','))
            videoproc.setmedium(videomedia)
            #eventh = GSHEETMediaEventHandler(rnum, cnum)
            #videoproc.subscribe(eventh)
            videomedia.setProcessAgent(videoproc)

        #audio media
        key = UIMapper.AUDIOSRC
        #get the column number
        ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        handle = self.__valueToURL(r[ccode])
        audio = BVMediaSource(handle, TalkJobKeys.BVMediaTypes.AUDIO)
        audiomedia = BVTalkMedium(audio)

        talk.addMedium(audiomedia)

        adirectives = (upldpattern[key])
        #invalidhandle = (handle == '') or (handle.find('ERROR')>=0)

        if UIMapper.isActive(adirectives) and (not status.isDone(key)):
            audioproc = MP3ID3SMediumProcAgent(key, adirectives.split(','))
            audioproc.setmedium(audiomedia)
            #eventh = GSHEETMediaEventHandler(rnum, cnum)
            #audioproc.subscribe(eventh)
            audiomedia.setProcessAgent(audioproc)

        #talk.addMedia(audiomedia)
        #talk.addMedia(videomedia)

        ################  Media  Host Agents creation ##########################
        # whenever a valid handle is available the host agent is not set
        # When other  upload commands will be implemented  this will also depend on the  command required

        host = None

        ##################### YouTube #######################
        key = UIMapper.YOUTUBE
        #get the column number
        ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        directives = upldpattern[key]
        handle = r[ccode]
        invalidhandle = (handle!='') or (handle.find('ERROR')>=0)

        # THE HANDLE NEED TO BE SET WHEN STATUS IS DONE:

        #if youtube is a host and no valid handle is available (not uploaded) then configure it
        if UIMapper.isActive(directives) and (not status.isDone(key)):
            host = YoutubeMediaHostAgent(key, videothumb, directives.split(','))
            #eventh = GSHEETMediaEventHandler(rnum,cnum)
            #host.subscribe(eventh)
            if UIMapper.isPrimary(directives):
                videomedia.setPrimaryHost(host)
            else:
                videomedia.appendHostAgent(host)

        # Vimeo
        key = UIMapper.VIMEO
        #get the column number
        #ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        directives = upldpattern[key]
        #handle = r[ccode]
        #invalidhandle = (handle!='') or (handle.find('ERROR')>=0)

        #if vimeo is a host and no valid handle is found then configure it
        if UIMapper.isActive(directives) and (not status.isDone(key)):
            host = VimeoMediaHostAgent( key, videothumb, directives.split(','))
            #eventh = GSHEETMediaEventHandler(rnum,cnum)
            #host.subscribe(eventh)
            if UIMapper.isPrimary(directives):
                videomedia.setPrimaryHost(host)
            else:
                videomedia.appendHostAgent(host)


        # S3 Audio
        key = UIMapper.S3AUDIO
        #get the column number
        #ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        directives = upldpattern[key]
        #handle = r[ccode]
        #invalidhandle = (handle!='') or (handle.find('ERROR')>=0)

        #if S3 is a host then configure it
        if UIMapper.isActive(directives) and (not status.isDone(key)):
            host = S3AudioMediaHostAgent(key, trainthumb, directives.split(','))
            #eventh = GSHEETMediaEventHandler(rnum,cnum)
            #host.subscribe(eventh)
            if UIMapper.isPrimary(directives):
                audiomedia.setPrimaryHost(host)
            else:
                audiomedia.appendHostAgent(host)


        # S3 Video
        key = UIMapper.S3VIDEO
        #get the column number
        ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        directives = upldpattern[key]
        #handle = r[ccode]
        #invalidhandle = (handle!='') or (handle.find('ERROR')>=0)

        #if S3 is a host then configure it
        if UIMapper.isActive(directives) and (not status.isDone(key)):
            host = S3VideoMediaHostAgent(key, videothumb, directives.split(','))
            #eventh = GSHEETMediaEventHandler(rnum,cnum)
            #host.subscribe(eventh)
            if UIMapper.isPrimary(directives):
                videomedia.setPrimaryHost(host)
            else:
                videomedia.appendHostAgent(host)

        # HWD Audio
        key = UIMapper.HWDAUDIO
        #get the column number
        ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        directives = upldpattern[key]
        #handle = r[ccode]
        #invalidhandle = (handle!='') or (handle.find('ERROR')==-1)

        #if hwd audio is a host then configure it
        if UIMapper.isActive(directives) and (not status.isDone(key)):
            host = HWDAudioMediaHostAgent(key, trainthumb, directives.split(','))
            #eventh = GSHEETMediaEventHandler(rnum,cnum)
            #host.subscribe(eventh)
            if UIMapper.isPrimary(directives):
                audiomedia.setPrimaryHost(host)
            else:
                audiomedia.appendHostAgent(host)

        # HWD Video
        key = UIMapper.HWDVIDEO
        #get the column number
        ccode = UIMapper.map[key]
        #cnum = UIMapper.cmap[ccode]
        directives = upldpattern[key]
        #handle = r[ccode]
        #invalidhandle = (handle!='') or (handle.find('ERROR')>=0)

        #if HWD video is a host then configure it
        if UIMapper.isActive(directives) and (not status.isDone(key)):
            host = HWDVideoMediaHostAgent(key, videothumb, directives.split(','))
            #eventh = GSHEETMediaEventHandler(rnum,cnum)
            #host.subscribe(eventh)
            if UIMapper.isPrimary(directives):
                videomedia.setPrimaryHost(host)
            else:
                videomedia.appendHostAgent(host)

        # Job creation
        # after alla agents are created we create the job and register the UI handler on the talk
        talk.subscribeAgentsHandler(GSHEETMediaEventHandler(talk, rnum))
        # WARNING: the job needs to created once all agents are in place, otherwise the subscriptions do not work
        # MUCH BETTER: include subscription in th addhost, add Proc methods !!!!!!!!!!!!!!!!!!!!
        #job = BVTalkJob(talk, action, status)

        # return the created talk job
        #return job
        return talk



    def openDB(self):
        global _WKS
        gc = gspread.login('bvoneclickupload@gmail.com', 'balancedview14')

        # Open a worksheet from spreadsheet with one shot
        log.stdout("opening DB...")
        _WKS = gc.open_by_key(SPREADSHEET).sheet1

        # initialize the column mapper to get column numbers from keys
        self.__initColumnMapper()

        log.stdout("... DB opened.")

        # load the rows from worksheet
        log.stdout ("loading jobs ...")
        self.__talkjobs = self.__getTalkJobs()
        log.stdout (" ...jobs loaded")

    def getTalkJobs(self): return self.__talkjobs


    def __getTalkJobs(self):
        # Get all the row-dictionaries and build talks
        # returns: a list of talk jobs

        #gdata: GET_ALL_RECORDS
        # Returns a list of dictionaries, all of them having:
        # the contents of the spreadsheet's first row of cells as keys
        # And each of these dictionaries holding - the contents of subsequent rows of cells as values.
        # Cell values are numericised (strings that can be read as ints or floats are converted).
        rows = _WKS.get_all_records()

        #skip the first 3 rows since they are headers
        jobs = []
        # the row 4 of the sheet is the third in the records, starting from 0
        recnum = 2
        #the row  4 of the sheet has num 4 for all cell setting proc of gdata
        rownum = 4
        while recnum < len(rows) :
            tj = self.__rowToTalk(rows[recnum], rownum)
            if tj != None :
                jobs.append(tj)
                log.stdout("Job %s loaded."%(tj.getID()))
            recnum = recnum+1
            rownum = rownum+1
        return jobs


    def __init__(self):



        return


################################################## UI section ######################################################


class GSHEETMediaEventHandler (BVMediaProcEventHandler, BVMediaHostEventHandler):
    ' we define only one handler for both proc and host agents and instantiate it for each talk job'

    def _getAgentCol(self,agent):
        key = agent.getKey()
        ccode = UIMapper.map[key]
        cnum = UIMapper.cmap[ccode]
        return cnum

    def _updateAgentCell(self, agent, string):
        col = self._getAgentCol(agent)
        _WKS.update_cell(self.row, col, string)

    def _updateStatusCell(self, agent, string):

        #find the status column number
        ccode = UIMapper.map[TalkJobKeys.STATUS]
        cnum = UIMapper.cmap[ccode]

        # calculate the new status string
        status = self.talk.getStatus()
        value = _statusToValue(status)
        _WKS.update_cell(self.row, cnum, value)





    def processSuccess(self, agent, handle, msg):
        #_WKS.update_cell(self.row, self.col, handle.toString())
        self._updateAgentCell(agent, handle.toString())
        self._updateStatusCell(agent, BVJobStatus.DONE)


    def processFailure(self, agent, msg):
        self._updateAgentCell(agent, "ERROR: %s"%(msg))
        self._updateStatusCell(agent, BVJobStatus.NOTDONE)


    def uploadSuccess(self, agent, handle, msg ):
         self._updateAgentCell(agent, handle.toString())
         self._updateStatusCell(agent, BVJobStatus.DONE)


    def uploadFailure(self, agent, msg):
         self._updateAgentCell(agent, "ERROR: %s"%(msg))
         self._updateStatusCell(agent, BVJobStatus.NOTDONE)


    def __init__(self, talk, trow):
        ' pass an instance of UIupdater instead'
        self.row = trow
        self.talk = talk
        #self.row = row
        #self.col = coltalk







