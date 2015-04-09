from ocuModel import *
from ocuUtils import *

_log = BVOneClickMessageLog('bvOneClickCT')


class OcuControlProcess (object):

    ### MAIN JOB PROCESSING ####
    @staticmethod
    def processJob(talk):
        assert isinstance(talk, BVTalkJob)

        # If the action is NOOP return immediately
        action = talk.getAction()
        if  action ==  BVTalkJob.NOOP: return

        # retrieves all the media of the talk
        medialist = talk.getMedia()

        #for each medium activate the associated   proc and host agents
        for m in medialist :
            assert isinstance (m, BVTalkMedium)

            # activate the media proc agent
            agent = m.getProcessAgent()
            if agent!=None: agent.processMedium()

            # activate the primary and other agents
            pagent = m.getPrimaryHost()
            oagents = m.getOtherHosts()

            # according to the operation invokes the action on each agent
            if action == BVTalkJob.UPLOAD:
                pagent.upload()
                for a in oagents:
                    a.upload()
            else:
                _log.stderr("This job action %s is not supported yet"% (action))
            # end agent invokation

        # end media list
    # end main job processing




