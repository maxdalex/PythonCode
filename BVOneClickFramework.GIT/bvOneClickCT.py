from bvOneClickDB import *
from bvOneClickUI import *

_log = BVOneClickMessageLog('bvOneClickCT')

class BVCTcommands (object):
    "list all commands parsed and executed"





class BVControlProcess (object):
    #While the hmedia host agents are part of the talk structure. The src processor are part of the control process
    # 28/2/15: changed and now the psource process are just agents of the media. So thi is not necessary
    #def __init__(self, srcproclist):
        #self.__srcproclist = srcproclist


    ### MAIN JOB PROCESSING ####
    def processjob(self, talk):
        assert isinstance(talk, BVTalk)



        # If the action is NOOP return immediately
        action = talk.getAction()
        if  action ==  BVTalk.NOOP: return

        #talk = talkjob.getTalk()

        assert isinstance(talk, BVTalk)
        medialist = talk.getMedia()

        #go through the media list and for each media acgtivate al the media hosts
        for m in medialist :
            assert isinstance (m, BVTalkMedia)

            # activate the media proc agent
            agent = m.getProcessAgent()
            if agent!=None: agent.processMedia()

            # activate the primary and other agents
            pagent = m.getPrimaryHost()
            oagents = m.getOtherHosts()

            # according to the operation invokes the action on each agent
            if action == BVTalk.UPLOAD:
                pagent.upload()
                for a in oagents:
                    a.upload()
            else:
                _log.stderr("This job action %s is not supported yet"% (action))
            # end agent invokation

        # end media list
    # end main job processing




