from  gspreadUIDB import *
from  mp3id3MediaProcAgent import *
from  mp4MediaProcAgent import *
import os.path

' This is the only module that needs to be modIfied for different implentTIONS OF THE FRAMEWORK'

################################ Framework Configuration ##################################################
class BVOneClickConf:
    'singletone and factory to provide the concrete instance of all abstract classes to the main of the BVOneClickFramework'

    def getDB(self): return DBgspread()
    def getUI(self): return UIgspread()
    def getAudioSrcProc(self): return MP3ID3SMediaProcAgent()
    def getVideoSrcProc(self): return MP4MediaProcAgent()


############################## Framework MAIN #################################
if __name__ == '__main__':

        conf = BVOneClickConf()
        #get concrete elements from the configurator: user interface, data base, src file processor, control
        ui = conf.getUI()
        db = conf.getDB()

        #Initialize the DB
        db.openDB()

        #get the list of jobs form the DB
        talkjobs = db.getTalkJobs()

        # intialize the UI with the list of talk jobs.
        ui.initialize(talkjobs)

        #specific source processors (not required, UIDB does everything)
        #audioproc = conf.getAudioSrcProc()
        #videoproc = conf.getVideoSrcProc()

        # create the job processor
        #ct = BVControlProcess([audioproc, videoproc])
        ct = BVControlProcess()

        for j in talkjobs:
            ct.processjob(j)

        ######## END POF MAIN ###############