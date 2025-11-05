#!/usr/bin/env python3
import sys
import os
import json
import LGMaster
import ProfilingAgentMaster
import ServerConfigurationMaster
import AutoPerf
import time
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class SoftwareBottleneckIdentificationKit:

    socket_connect_info=None
    load_test_folder=""
    bottleneck_conf={}
    load_generator_master_obj=""
    processMetrics_vs_cores={}

    def start(self,socket_connect_info):
        self.socket_connect_info=socket_connect_info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.load_test_folder = "bottleneck_identifation_output"+"/"+"loadTesting_"+timestamp 
        os.makedirs(self.load_test_folder)
        bottleneck_configurations="input-configurations/bottleneck-identification-conf.json"
        with open(bottleneck_configurations,'rb') as file:
            bottleneck_conf_content=file.read()
        bottleneck_conf_json_content=bottleneck_conf_content.decode('utf-8')
        self.bottleneck_conf=json.loads(bottleneck_conf_json_content)
        self.runLoadTest()

    def runLoadTest(self):
        cores_details=self.bottleneck_conf['coresDetails']
        user_session=self.bottleneck_conf['sessionDetails']
        load_generator_details=self.bottleneck_conf['loadGeneratorDetails']
        processes_details=self.bottleneck_conf['processToProfileDetails']
        initial_resource_configuration_details=self.bottleneck_conf['baselineResourceConfigurationDetails']
        resource_configuration_details=self.bottleneck_conf['softwareResourceConfigurationDetails']

        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster()
        self.load_generator_master_obj=LGMaster.LGMaster()
        self.load_generator_master_obj.initialize(load_generator_details["name"],user_session["filePath"],profiling_agent_master_obj,"softwareBottleneckIdentification")
        profiling_agent_master_obj.initialize(processes_details["names"],self.socket_connect_info)
        server_configuration_master_obj=ServerConfigurationMaster.ServerConfigurationMaster()

        for process_name in processes_details["names"]:
            self.processMetrics_vs_cores[process_name]={"cpu_service_demad":{},"CPUPercentage":{},"#_of_worker_processes_threads":{}}

        server_configuration_master_obj.setCores(cores_details['noOfCores'],self.socket_connect_info)

        for resource_name in initial_resource_configuration_details:
            server_configuration_master_obj.setSoftwareResource(initial_resource_configuration_details[resource_name],self.socket_connect_info)

        autoperf_obj=AutoPerf.AutoPerf()
        autoperf_obj.initialize(user_session['thinkTime'],cores_details['noOfCores'],self.load_generator_master_obj,profiling_agent_master_obj)
        baseline_throughput=autoperf_obj.automatedLoadTesting()
        print(baseline_throughput)
        for resource_name in resource_configuration_details:

            for i_resource_name in initial_resource_configuration_details:
                server_configuration_master_obj.setSoftwareResource(initial_resource_configuration_details[i_resource_name],self.socket_connect_info)
            max_throughput=0
            throughput_list=[]
            resource_value_list=[]
            for resource_value in range(resource_configuration_details[resource_name]['valueRange']['minValue'],resource_configuration_details[resource_name]['valueRange']['maxValue'],resource_configuration_details[resource_name]['valueRange']['step']):
                print(resource_value)
                resource_details={"name":"","filePath":"","reqExp":"","value":0,"commands":"","timeWait":5}
                resource_details['name']=resource_configuration_details[resource_name]['name']
                resource_details['filePath']=resource_configuration_details[resource_name]['filePath']
                resource_details['reqExp']=resource_configuration_details[resource_name]['reqExp']
                resource_details['value']=resource_value
                resource_details['commands']=resource_configuration_details[resource_name]['commands']
                resource_details['timeWait']=resource_configuration_details[resource_name]['timeWait']

                server_configuration_master_obj.setSoftwareResource(resource_details,self.socket_connect_info)

                throughput=autoperf_obj.automatedLoadTesting()
                throughput_list.append(throughput)
                resource_value_list.append(resource_value)

                max_throughput=max(throughput,max_throughput)
                
            print(max_throughput)
            self.plotBottleneckGraph(resource_value_list,throughput_list,resource_name,resource_name)
            
            if(max_throughput>baseline_throughput*cores_details['SoftResourceBottleneckThreshold']):
                print(max_throughput)
                print(resource_name+" is the bottleneck")
                return

        print("Mentioned soft resources are not the bottleneck")

    def plotBottleneckGraph(self,x_axis,y_axis,plot_title,y_axis_title):
        file_name=self.load_test_folder+"/"+plot_title
        plt.figure(figsize=(8, 5))
        plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b', label='Values')
        plt.xlabel(y_axis_title)
        plt.ylabel("Throughput (req/sec)")
        plt.title(plot_title)
        plt.grid(True)
        plt.savefig(file_name)
        plt.close()

