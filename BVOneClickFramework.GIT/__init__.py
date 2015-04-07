from bvOneClickConfig import *
import os.path



############################## Framework MAIN #################################
# This allows the system to be run as a batch executable, directly fetching jobs from the
# Job Manager DataBase. For interactive behaviour see processJob() method in CT module
if __name__ == '__main__':

        # retrieves ui and db from the framework configuration
        ui =  BVOneClickConf.getUI()
        db =  BVOneClickConf.getDB()

        #Initialize the DB
        db.openDB()

        #get the list of jobs form the DB
        talkjobs = db.getTalkJobs()

        # intialize the UI with the list of talk jobs.
        ui.initializeUI(talkjobs)

        # create the job processor
        ct = BVOneClickConf.getCT()

        for j in talkjobs:
            ct.processJob(j)

################################################ END OF MAIN ###############