import win32serviceutil
import win32event
import win32service
import win32api
import servicemanager
import time
import cabsagent
import sys
import os
#from sched import scheduler

class AgentService(win32serviceutil.ServiceFramework):
    #_svc_name_ = "aservice"
    #_svc_display_name_ = "a service - it does nothing"
    #_svc_description_ = "foo bar"
    _svc_name_ = "CABS_Agent"
    _svc_display_name_ = "CABS Agent"
    _svc_description_ = "The Agent reporting to the CABS Broker"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        cabsagent.stop()
    
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        cabsagent.start()
    
    # These methods can be used instead for testing.

#    def __init__(self, args):
#        win32serviceutil.ServiceFramework.__init__(self, args)
#        #logfile = os.path.join(os.getenv('APPDATA'), 'cabsagent.log')
#        #print("log location:", logfile)
#        #logging.basicConfig(filename=logfile, format='%(asctime)s %(message)s',
#        #                    level=logging.DEBUG)
#        #logging.info("AgentService.__init__()")
#        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#        #self.stop_requested = False
#
#    def SvcStop(self):
#        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#        win32event.SetEvent(self.hWaitStop)
#    
#    def SvcDoRun(self):
#        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
#        import servicemanager
#        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
#                              servicemanager.PYS_SERVICE_STARTED,
#                              (self._svc_name_, ''))
#        self.timeout = 3000
#
#        while 1:
#            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
#            if rc == win32event.WAIT_OBJECT_0:
#                servicemanager.LogInfoMsg("aservice - STOPPED")
#                break
#            else:
#                servicemanager.LogInfoMsg("aservice - is alive and well")
#
#def ctrlHandler(ctrlType):
#    return True
    
if __name__ == "__main__":
    #win32api.SetConsoleCtrlHandler(ctrlHandler, True)   
    #win32serviceutil.HandleCommandLine(aservice)
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AgentService)
