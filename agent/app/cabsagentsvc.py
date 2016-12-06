import win32serviceutil
import win32event
import win32service
import win32api
import servicemanager
import time
import cabsagent
import sys
import os

class AgentService(win32serviceutil.ServiceFramework):
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
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AgentService)
