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

class HardwareBottleneckIdentificationKit:

    scalability_conf={}
    metrics_vs_cores={"Throughput":{},"OverallCPUPercentage":{},"userCPUTime":{},"sysCPUTime":{},"responseTime":{},"failureRate":{},"observedThinkTime":{},"ctxSwitches":{},"virtualMemoryUsedPercentage":{},"diskUsedPercentage":{},"swapMemoryUsedPercentage":{},"calculatedCPUServiceDemand":{},"observedCPUServiceDemand":{},"LLC-loads":{},"LLC-load-misses":{},"LLC-stores":{},"LLC-store-misses":{},"test-duration":{}}
    load_generator_master_obj=""
    socket_connect_info=None
    maxThroughput_vs_cores={}
    processMetrics_vs_cores={}
    load_test_folder=""
    output_file_name=""

    def start(self,socket_connect_info):
        self.socket_connect_info=socket_connect_info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.load_test_folder = "memory_bottleneck_output"+"/"+"loadTesting_"+timestamp 
        os.makedirs(self.load_test_folder)
        scalability_configurations="input-configurations/memory-bottleneck-identification.json"
        with open(scalability_configurations,'rb') as file:
            scalability_conf_content=file.read()
        scalability_conf_json_content=scalability_conf_content.decode('utf-8')
        self.scalability_conf=json.loads(scalability_conf_json_content)
        self.runLoadTest()

    def runLoadTest(self):
        cores_details=self.scalability_conf['coresDetails']
        user_session=self.scalability_conf['sessionDetails']
        load_generator_details=self.scalability_conf['loadGeneratorDetails']
        processes_details=self.scalability_conf['processToProfileDetails']
        resource_configuration_details=self.scalability_conf['baselineResourceConfigurationDetails']

        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster()
        self.load_generator_master_obj=LGMaster.LGMaster()
        self.load_generator_master_obj.initialize(load_generator_details["name"],user_session["filePath"],profiling_agent_master_obj,"perfProfiling")
        profiling_agent_master_obj.initialize(processes_details["names"],self.socket_connect_info)
        server_configuration_master_obj=ServerConfigurationMaster.ServerConfigurationMaster()

        for process_name in processes_details["names"]:
            self.processMetrics_vs_cores[process_name]={"cpu_service_demad":{},"CPUPercentage":{},"#_of_worker_processes_threads":{},"memory_percentage":{},"LLC-loads":{},"LLC-load-misses":{},"LLC-stores":{},"LLC-store-misses":{}}

        for resource_name in resource_configuration_details:
            server_configuration_master_obj.setSoftwareResource(resource_configuration_details[resource_name],self.socket_connect_info)

        for cores in cores_details['cores']:
            server_configuration_master_obj.setCores(cores,self.socket_connect_info)
            autoperf_obj=AutoPerf.AutoPerf()
            autoperf_obj.initialize(user_session['thinkTime'],cores,self.load_generator_master_obj,profiling_agent_master_obj)
            test_start_time=time.time()
            throughput=autoperf_obj.automatedLoadTesting()
            test_end_time=time.time()
            self.maxThroughput_vs_cores[cores]=throughput
            self.metrics_vs_cores["Throughput"][cores]=self.maxThroughput_vs_cores[cores]
            self.metrics_vs_cores["responseTime"][cores]=autoperf_obj.max_response_time
            self.metrics_vs_cores["failureRate"][cores]=autoperf_obj.max_failure_rate
            self.metrics_vs_cores["observedThinkTime"][cores]=autoperf_obj.max_observed_think_time
            self.metrics_vs_cores["OverallCPUPercentage"][cores]=autoperf_obj.application_resource_usage["OverallCPUPercentage"]
            self.metrics_vs_cores["userCPUTime"][cores]=autoperf_obj.application_resource_usage["userCPUTime"]
            self.metrics_vs_cores["sysCPUTime"][cores]=autoperf_obj.application_resource_usage["sysCPUTime"]
            self.metrics_vs_cores["ctxSwitches"][cores]=autoperf_obj.application_resource_usage["ctxSwitches"]
            self.metrics_vs_cores["virtualMemoryUsedPercentage"][cores]=autoperf_obj.application_resource_usage["virtualMemoryUsedPercentage"]
            self.metrics_vs_cores["diskUsedPercentage"][cores]=autoperf_obj.application_resource_usage["diskUsedPercentage"]
            self.metrics_vs_cores["swapMemoryUsedPercentage"][cores]=autoperf_obj.application_resource_usage["swapMemoryUsedPercentage"]
            self.metrics_vs_cores["LLC-loads"][cores]=autoperf_obj.application_perf_resource_usage["LLC-loads"]
            self.metrics_vs_cores["LLC-load-misses"][cores]=autoperf_obj.application_perf_resource_usage["LLC-load-misses"]
            self.metrics_vs_cores["LLC-stores"][cores]=autoperf_obj.application_perf_resource_usage["LLC-stores"]
            self.metrics_vs_cores["LLC-store-misses"][cores]=autoperf_obj.application_perf_resource_usage["LLC-store-misses"]
            self.metrics_vs_cores["calculatedCPUServiceDemand"][cores]=(cores*self.metrics_vs_cores["OverallCPUPercentage"][cores])/(self.metrics_vs_cores["Throughput"][cores]*100)
            self.metrics_vs_cores["observedCPUServiceDemand"][cores]=0
            self.metrics_vs_cores["test-duration"][cores]=test_end_time-test_start_time
            count=0
            print(autoperf_obj.process_resource_usage)
            for process_name in processes_details["names"]:
                self.processMetrics_vs_cores[process_name]["cpu_service_demad"][cores]=autoperf_obj.max_processes_cpu_service_demad[count]
                self.processMetrics_vs_cores[process_name]["CPUPercentage"][cores]=(autoperf_obj.process_resource_usage[process_name]["CPUPercentage"])/cores
                self.processMetrics_vs_cores[process_name]["#_of_worker_processes_threads"][cores]=(autoperf_obj.process_resource_usage[process_name]["#_of_worker_processes_threads"])
                self.processMetrics_vs_cores[process_name]["memory_percentage"][cores]=(autoperf_obj.process_resource_usage[process_name]["memory_percentage"])
                self.processMetrics_vs_cores[process_name]["LLC-loads"][cores]=(autoperf_obj.process_perf_resource_usage[process_name]["LLC-loads"])
                self.processMetrics_vs_cores[process_name]["LLC-load-misses"][cores]=(autoperf_obj.process_perf_resource_usage[process_name]["LLC-load-misses"])
                self.processMetrics_vs_cores[process_name]["LLC-stores"][cores]=(autoperf_obj.process_perf_resource_usage[process_name]["LLC-stores"])
                self.processMetrics_vs_cores[process_name]["LLC-store-misses"][cores]=(autoperf_obj.process_perf_resource_usage[process_name]["LLC-store-misses"])
                self.metrics_vs_cores["observedCPUServiceDemand"][cores]=self.metrics_vs_cores["observedCPUServiceDemand"][cores]+self.processMetrics_vs_cores[process_name]["cpu_service_demad"][cores]
                count=count+1

        for metric_name in self.metrics_vs_cores:
                x_axis=list(self.metrics_vs_cores[metric_name].keys())
                y_axis=list(self.metrics_vs_cores[metric_name].values())
                plot_title=metric_name+"  vs cores"
                self.plotmetricsGraph(x_axis,y_axis,plot_title,"# of cores",metric_name)
            
        for process_name in processes_details["names"]:
            for metric_name in self.processMetrics_vs_cores[process_name]:
                x_axis=list(self.processMetrics_vs_cores[process_name][metric_name].keys())
                y_axis=list(self.processMetrics_vs_cores[process_name][metric_name].values())
                plot_title=process_name+"_"+metric_name+"  vs cores"
                self.plotmetricsGraph(x_axis,y_axis,plot_title,"# of cores",process_name+"_"+metric_name)

        self.resourceUsageProfiling(processes_details,cores_details)

    def resourceUsageProfiling(self,processes_details,cores_details):
        resource_details_names=["LLC-loads","LLC-load-misses","LLC-stores","LLC-store-misses"]
        for process_name in processes_details["names"]:
            for resource in resource_details_names:
                for cores in cores_details['cores']:
                    if self.processMetrics_vs_cores[process_name][resource][1]!=0 and cores!=1:
                        temp=(self.processMetrics_vs_cores[process_name][resource][cores]/self.processMetrics_vs_cores[process_name][resource][1])
                        if(temp>(cores*cores_details['LLCInflationFactor'])):
                            print(resource+" of "+process_name+" doesn't have linear increment with inflation factor"+str(temp))
        
        for resource in resource_details_names:
            for cores in cores_details['cores']:
                if self.metrics_vs_cores[resource][1]!=0 and cores!=1:
                    temp=self.metrics_vs_cores[resource][cores]/self.metrics_vs_cores[resource][1]
                    if(temp>(cores*cores_details['LLCInflationFactor'])):
                        print(resource+" doesn't scale linear with inflation factor"+str(temp))

        for cores in cores_details['cores']:
            if(self.metrics_vs_cores["observedCPUServiceDemand"][cores]>self.metrics_vs_cores["calculatedCPUServiceDemand"][cores] or self.metrics_vs_cores["observedCPUServiceDemand"][cores]<self.metrics_vs_cores["calculatedCPUServiceDemand"][cores]):
                print("Observed CPU Service Demand is not equal to Calculated CPU Service Demand at core"+str(cores))

    def plotScalabilityGraph(self):
        file_name=self.load_test_folder+"/"+"scalability"
        x_axis=list(self.maxThroughput_vs_cores.keys())
        y_axis=list(self.maxThroughput_vs_cores.values())
        plt.figure(figsize=(8, 5))
        plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b', label='Values')
        plt.xlabel('# of cores')
        plt.ylabel('Throughput(req/sec)')
        plt.title('Throughput(req/sec) vs #cores')
        plt.grid(True)
        plt.savefig(file_name)
        plt.close()

    def plotmetricsGraph(self,x_axis,y_axis,plot_title,x_axis_title,y_axis_title):
        file_name=self.load_test_folder+"/"+plot_title
        plt.figure(figsize=(8, 5))
        plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b', label='Values')
        plt.xlabel(x_axis_title)
        plt.ylabel(y_axis_title)
        plt.title(plot_title)
        plt.grid(True)
        plt.savefig(file_name)
        plt.close()
