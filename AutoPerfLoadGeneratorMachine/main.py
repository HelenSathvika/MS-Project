#!/usr/bin/env python3
#Import all required libraries 
import sys
import os
import time
import ThreadPoolClassificationKit
import SystemUnderTest
import ScalabilityProfilingKit
import MisconfiguredSoftResourceIdentificationKit
import LLCBottleneckDetectionKit

class MasterController: #AutoPerf++ Master Controller starts from here
    def __init__(self):

        self.system_undertest_obj=SystemUnderTest.SystemUnderTest() #Create an instance/object of SystemUnderTest class 
        self.system_undertest_obj.setServerDetails() #Store server configuration details in variables 
        print("Connecting to server")
        self.system_undertest_obj.startServer() #Start the Server Side Agent
        time.sleep(5) #Wait for 5 seconds after Starting Server Side Agent, so that, proper communication will happen b/w Master Controller and Server Side Agent
        self.system_undertest_obj.connectToServer() #Connect to the Server Side Agent

        self.whatToDo=int(sys.argv[1]) #In which mode the user wants to run AutoPerf++

        self.selection={
            1: self.scalabilityProfiling,
            2: self.llcBottleneckDetection,
            3: self.misconfiguredSoftResourceIdentification,
            4: self.threadPoolClassification
            }

        self.needToDo=self.selection.get(self.whatToDo,self.invalidOption)
        return self.needToDo()

    def scalabilityProfiling(self): #Start Scalability Profiling Mode
        scalability_profiling_obj=ScalabilityProfilingKit.ScalabilityProfilingKit()
        scalability_profiling_obj.start(self.system_undertest_obj.socket_connect_info) #Start
        self.system_undertest_obj.closeServerConnection()
    
    def llcBottleneckDetection(self): #Start LLC Cache Bottleneck Detection Mode
        bottleneck_identification_obj=LLCBottleneckDetectionKit.LLCBottleneckDetectionKit()
        bottleneck_identification_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()

    def misconfiguredSoftResourceIdentification(self): #Start Misconfigured Soft Resource Bottleneck Identification Mode 
        bottleneck_identification_obj=MisconfiguredSoftResourceIdentificationKit.MisconfiguredSoftResourceIdentificationKit()
        bottleneck_identification_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()
    
    def threadPoolClassification(self): #Start Idle/Busy Thread Classification Mode
        potential_bottlenecks_obj=ThreadPoolClassificationKit.ThreadPoolClassificationKit()
        potential_bottlenecks_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()
    
    def invalidOption(self):
        print("Invlaid Option")

if __name__ == "__main__":
    start=MasterController() #AutoPerf++ tool is begins
