#!/usr/bin/env python3
import sys
import os
import time
# script_dir = "/home/helen/Desktop/Helen/autoperfsb"
# os.chdir(script_dir)
# sys.path.append(script_dir)
import ManualLoadTestingTimeDurationKit
import ManualLoadTestingKit
#import AutomatedLoadTestingKit
import PotentialProcessBottlenecksKit
import SystemUnderTest
import ScalabilityProfilingKit
import SoftwareBottleneckIdentificationKit
import HardwareBottleneckIdentificationKit

class Main:
    def __init__(self):

        self.system_undertest_obj=SystemUnderTest.SystemUnderTest()
        self.system_undertest_obj.setServerDetails()
        print("Connecting to server")
        self.system_undertest_obj.startServer()
        time.sleep(5)
        self.system_undertest_obj.connectToServer()

        self.whatToDo=int(sys.argv[1])

        self.selection={
            1: self.manualLoadTestingWithTimeDuration,
            2: self.manualLoadTestingWithoutTimeDuration,
            3: self.automatedLoadTesting,
            4: self.identifyingPotentialProcessBottleneck,
            5: self.scalabilityProfiling,
            6: self.softwareBottleneckIdentification,
            7: self.hardwareBottleneckIdentification
            }

        self.needToDo=self.selection.get(self.whatToDo,self.invalidOption)
        return self.needToDo()

    def manualLoadTestingWithTimeDuration(self):
        manual_load_testing_obj=ManualLoadTestingTimeDurationKit.ManualLoadTestingTimeDurationKit()
        manual_load_testing_obj.start()
        self.system_undertest_obj.closeServerConnection()
    
    def manualLoadTestingWithoutTimeDuration(self):
        manual_load_testing_obj=ManualLoadTestingKit.ManualLoadTestingKit()
        manual_load_testing_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()

    def automatedLoadTesting(self):
        automated_load_testing_obj=AutomatedLoadTestingKit.AutomatedLoadTestingKit()
        automated_load_testing_obj.start()
        self.system_undertest_obj.closeServerConnection()

    def identifyingPotentialProcessBottleneck(self):
        potential_bottlenecks_obj=PotentialProcessBottlenecksKit.PotentialProcessBottlenecksKit()
        potential_bottlenecks_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()

    def scalabilityProfiling(self):
        scalability_profiling_obj=ScalabilityProfilingKit.ScalabilityProfilingKit()
        scalability_profiling_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()

    def softwareBottleneckIdentification(self):
        bottleneck_identification_obj=SoftwareBottleneckIdentificationKit.SoftwareBottleneckIdentificationKit()
        bottleneck_identification_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()

    def hardwareBottleneckIdentification(self):
        bottleneck_identification_obj=HardwareBottleneckIdentificationKit.HardwareBottleneckIdentificationKit()
        bottleneck_identification_obj.start(self.system_undertest_obj.socket_connect_info)
        self.system_undertest_obj.closeServerConnection()
    
    def invalidOption(self):
        print("Invlaid Option")

if __name__ == "__main__":
    start=Main()


    

    