import gspread
from ocuModel import *
from ocuControl import *
from ocuUtils import *


SPREADSHEET= '1dwjdmi77m9gVFts5WYawy_k11LekmB7ejjo-5VkU0QQ'
LISTDELIMITER =','

YOUTUBE = 'youtube'
VIMEO = 'vimeo'
HWDVIDEO = 'hwdvideo'
HWDAUDIO = 'hwdaudio'
S3VIDEO = 's3video'
S3AUDIO = 's3audio'

log = BVOneClickMessageLog('gSheetJobManager')

#THE worksheet handle to gdata. Global to the module
_WKS = None

##################### Shortcuts to OCU's costants ###############################
EXTRACTAUDIO = BVMediumProcAgent.EXTRACTAUDIO
PRIMARYHOST = BVMediumHostAgent.PRIMARYHOST
UPLOAD = BVMediumHostAgent.UPLOAD
REMOTELNK = BVMediumHostAgent.REMOTELNK
VIDEOTHUMB = BVMediumHostAgent.VIDEOTHUMB
TRAINTHUMB = BVMediumHostAgent.TRAINTHUMB

#sheet columns names


"""
YOUTUBE = Names.YOUTUBE
VIMEO = BVOneClickConf.VIMEO
HWDAUDIO = BVOneClickConf.HWDAUDIO
HWDVIDEO = BVOneClickConf.HWDVIDEO
S3AUDIO = BVOneClickConf.S3AUDIO
S3VIDEO = BVOneClickConf.S3VIDEO
"""

VIDEOSRC = BVMediumProcAgent.VIDEOSOURCE
AUDIOSRC = BVMediumProcAgent.AUDIOSOURCE

ID = BVTalkDescriptor.ID
ACTION =  BVTalkJob.ACTION
STATUS = BVTalkJob.STATUS
DATE = BVTalkDescriptor.DATE
TRAINER = BVTalkDescriptor.TRAINER
CONTEXT = BVTalkDescriptor.CONTEXT
TITLE = BVTalkDescriptor.TITLE
LANGUAGE = BVTalkDescriptor.LANGUAGE
TAGS = BVTalkDescriptor.TAGS
CATEGORY = BVTalkDescriptor.CATEGORY
QUOTE = BVTalkDescriptor.QUOTE
ACCESS = BVTalkDescriptor.ACCESS
EDITOR = BVTalkDescriptor.EDITOR
EXCPTCOMP = BVTalkDescriptor.EXCPTCOMP

AUDIO = BVMediaTypes.AUDIO
VIDEO = BVMediaTypes.VIDEO
UPLDPATTERN = 'upldpattern'#I need to understand why this is different


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




class GSheetMapper (object):
    'It manages the mapping between parameters and columns in the sheet picking by key rather than number'
    """
    In the sheet there is a mapping row (the first one) giving a fixed numeric code for each column. If new columns are added
    Or old ones are changed in position, the code remain the same and so the class methods are able to pick
    the right column number. We also have two mapings needed: col cod --> record field, col cod --> sheet column number
    Since we use get_all_records records are fetched as dictonary rather than a list. See below.
    """

    # DB keys are used  when available  UI specific KEY not provided by the DB layer are following


    # This dictionary translates column codes in column numbers. It is dynamically initialized within the UI
    cmap = {}

    # This dictionary translates the column codes into standard keys. This allows to change the labels of
    # the column in the sheet without affecting the program, which uses its own label system consistently
    map = {
            ID: '1',
            BVTalkJob.ACTION: '2',
            BVTalkJob.STATUS: '3',
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
        res =  PRIMARYHOST in list
        return res

    @staticmethod
    def isActive(selfdir):
        return (selfdir != '')


    #Dictionary of directives for the agents. Where the value is '' the agent is not activated
    updirectives = {

        UPLD_YOUTUBE: {
            AUDIO: {
                AUDIOSRC: "%s" % (EXTRACTAUDIO),
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
            
        },
        UPLD_VIMEO: {
            AUDIO: {
                AUDIOSRC: "%s" % (EXTRACTAUDIO),
                HWDAUDIO: "%s,%s" % (UPLOAD, PRIMARYHOST),
                S3AUDIO: ''
            },
            VIDEO: {
                VIDEOSRC:'',
                YOUTUBE:'',
                VIMEO:  "%s,%s" % (UPLOAD, PRIMARYHOST),
                HWDVIDEO: "%s,%s" % (UPLOAD, REMOTELNK),
                S3VIDEO: ''
            }
        },
        UPLD_HWD :{
            AUDIO: {
                AUDIOSRC: "%s" % (EXTRACTAUDIO),
                HWDAUDIO: "%s,%s" % (UPLOAD, PRIMARYHOST),
                S3AUDIO: ''
            },
            VIDEO: {
                VIDEOSRC:'',
                YOUTUBE:'',
                VIMEO:  '',
                HWDVIDEO: "%s,%s" % (UPLOAD, PRIMARYHOST),
                S3VIDEO: ''
            }
        }

    }





class GSheetJobManager (OcuJobManagerInterface) :
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


    def __initColumnMapper(self):
        #read the first row
        value_list = _WKS.row_values(1)
        cnum = 1
        for v in value_list:
            GSheetMapper.cmap[v] =cnum
            cnum = cnum+1


    @staticmethod
    def __getTalkDescriptorStringDic(r):
        'it loads desc with a dictionary of strings taken from the row'

        desc = {}

        key = ID
        desc[key] = r[GSheetMapper.map[key]]

        key = DATE
        desc[key] = r[GSheetMapper.map[key]]

        key = TRAINER
        desc[key] = r[GSheetMapper.map[key]]

        key = CONTEXT
        desc[key] = r[GSheetMapper.map[key]]

        key = EDITOR
        desc[key] = r[GSheetMapper.map[key]]

        key = LANGUAGE
        desc[key] = r[GSheetMapper.map[key]]

        key = QUOTE
        desc[key] = r[GSheetMapper.map[key]]

        key = TITLE
        desc[key] = r[GSheetMapper.map[key]]

        key = TAGS
        desc[key] = r[GSheetMapper.map[key]]

        key = CATEGORY
        desc[key] = r[GSheetMapper.map[key]]

        key = ACCESS
        desc[key] = r[GSheetMapper.map[key]]

        key = EXCPTCOMP
        desc[key] = r[GSheetMapper.map[key]]

        return desc



    def __rowToTalk(self, r, rnum):
        'r is a row of the spreadsheet in form of a dictionary'

        # If the action is SKIP or NOOP it returns immediately
        action = r[GSheetMapper.map[BVTalkJob.ACTION]]
        if (action== BVTalkJob.SKIP or action == BVTalkJob.NOOP or action == '' ): return None

        # create Status
        status = self.__valueToStatus(r[GSheetMapper.map[BVTalkJob.STATUS]])

        # create Talk descriptor
        sdesc = GSheetJobManager.__getTalkDescriptorStringDic(r)
        talkdesc = BVTalkDescriptor()
        talkdesc.importFromStringDict(sdesc)

        # get video thumb URL
        videothumb = r[GSheetMapper.map[VIDEOTHUMB]]
        
        #get video source URL
        videosrc = r[GSheetMapper.map[VIDEOSRC]]
        
        #get audio src URL
        audiosrc = r[GSheetMapper.map[AUDIOSRC]]

        #create upoad pattern
        pattername = r[GSheetMapper.map[UPLDPATTERN]]
        patterndict = GSheetMapper.updirectives[pattername]
        agentsptrn = OcuUploadPattern(patterndict)
        
        # create the Talk Job
        talkjob = OcuTalkJobFactory.createTalkJob(action, status, talkdesc, videosrc, videothumb,agentsptrn,audiosrc)

        # Subscribe the gsheet event handler on all agents of the talk
        eventHandler = GsheetTalkEventHandler(talkjob, rnum)
        talkjob.subscribeAgentsHandler(eventHandler)

        # return the created talk job
        return talkjob



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

        # gdata: GET_ALL_RECORDS
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



class GsheetTalkEventHandler (BVAgentEventHandlerInterface):
    'This is the handler listening for how the agents of the talk have done after their actions'

    def _getAgentCol(self,agent):
        key = agent.getID()
        ccode = GSheetMapper.map[key]
        cnum = GSheetMapper.cmap[ccode]
        return cnum

    def _updateAgentCell(self, agent, string):
        col = self._getAgentCol(agent)
        _WKS.update_cell(self.row, col, string)

    def _updateStatusCell(self, agent, string):

        #find the status column number
        ccode = GSheetMapper.map[BVTalkJob.STATUS]
        cnum = GSheetMapper.cmap[ccode]

        # calculate the new status string
        status = self.talk.getStatus()
        value = _statusToValue(status)
        _WKS.update_cell(self.row, cnum, value)


    def handleSuccess(self, agent, handle, msg):
        self._updateAgentCell(agent, handle.toString())
        self._updateStatusCell(agent, BVJobStatus.DONE)


    def handleFailure(self, agent, msg):
        self._updateAgentCell(agent, "ERROR: %s"%(msg))
        self._updateStatusCell(agent, BVJobStatus.NOTDONE)


    def __init__(self, talk, trow):
        ' pass an instance of UIupdater instead'
        self.row = trow
        self.talk = talk
