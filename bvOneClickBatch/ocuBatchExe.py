from ocuFrameworkAPI import *
from  gSheetJobManager import *


############################## Framework MAIN #################################
# This allows the system to be run as a batch executable, directly fetching jobs from the
# Job Manager DataBase. For interactive behaviour see processJob() method in BvOneClickFramework module
if __name__ == '__main__':

        #create an instance of the framework
        ocu = BVOneClickFramework()

        # retrieves job manager
        jman =  GSheetJobManager()

        #Initialize the DB
        jman.openDB()

        #get the list of jobs form the DB
        talkjobs = jman.getTalkJobs()

        # process all jobs
        for j in talkjobs:
            ocu.processJob(j)

################################################ END OF MAIN ###############