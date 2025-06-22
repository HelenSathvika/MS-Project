#!/usr/bin/env python3
#Import all required libraries 
import sys
import os
import json
import LGMaster
import ProfilingAgentMaster
import ServerConfigurationMaster
import CapacityAnalysis
import time
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


class ScalabilityProfilingKit:

    scalability_conf={}
    load_generator_master_obj=""
    socket_connect_info=None
    maxThroughput_vs_cores={}
    metrics_vs_cores={"Throughput":{},"OverallCPUPercentage":{},"userCPUTime":{},"sysCPUTime":{},"responseTime":{},"failureRate":{},"observedThinkTime":{},"ctxSwitches":{},"virtualMemoryUsedPercentage":{},"diskUsedPercentage":{},"swapMemoryUsedPercentage":{},"calculatedCPUServiceDemand":{},"observedCPUServiceDemand":{},"test-duration":{}}
    processMetrics_vs_cores={}
    load_test_folder=""
    output_file_name=""

    def start(self,socket_connect_info): #Start Scalability Profiling Mode 
        self.socket_connect_info=socket_connect_info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #Create a unique name folder to store the ouput graphs of this run 
        self.load_test_folder = "scalability_output"+"/"+"loadTesting_"+timestamp 
        os.makedirs(self.load_test_folder)
        scalability_configurations="input-configurations/scal-prof-conf.json"
        with open(scalability_configurations,'rb') as file: # Read Scalability profiling Configuration File
            scalability_conf_content=file.read()
        scalability_conf_json_content=scalability_conf_content.decode('utf-8')
        self.scalability_conf=json.loads(scalability_conf_json_content)
        self.runLoadTest() #Start the scalability profiling of the application

    def runLoadTest(self):
        #Collect all the user input specification details in a variable
        cores_details=self.scalability_conf['coresDetails'] #Core Details
        user_session=self.scalability_conf['sessionDetails'] #User Session Details 
        load_generator_details=self.scalability_conf['loadGeneratorDetails'] #Load Generator Details
        processes_details=self.scalability_conf['processToProfileDetails'] #Process To Profile Details
        resource_configuration_details=self.scalability_conf['baselineResourceConfigurationDetails'] #Baseline Soft Resource Configuration Details

        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster() #Create an instance of Profiling Agent Master
        self.load_generator_master_obj=LGMaster.LGMaster()  #Create an instance of Load Geneator Master
        self.load_generator_master_obj.initialize(load_generator_details["name"],user_session["filePath"],profiling_agent_master_obj,"ScalabilityProfiling") #Intialize Profiling Agent Master
        profiling_agent_master_obj.initialize(processes_details["names"],self.socket_connect_info) #Intialize Load Generator Master
        server_configuration_master_obj=ServerConfigurationMaster.ServerConfigurationMaster() #Create an instance of Server Configuration Master

        for process_name in processes_details["names"]:
            self.processMetrics_vs_cores[process_name]={"cpu_service_demad":{},"CPUPercentage":{},"#_of_worker_processes_threads":{},"memory_percentage":{}}

        for resource_name in resource_configuration_details: #For each baseline soft resource configurations
            server_configuration_master_obj.setSoftwareResource(resource_configuration_details[resource_name],self.socket_connect_info) #Set the baseline soft resource value

        for cores in cores_details['cores']: #For each core level
            server_configuration_master_obj.setCores(cores,self.socket_connect_info) #Set the core level
            CapacityAnalysis_obj=CapacityAnalysis.CapacityAnalysis() #Create an instance of CapacityAnalysis
            CapacityAnalysis_obj.initialize(user_session['thinkTime'],cores,self.load_generator_master_obj,profiling_agent_master_obj) #Initialize capacity analysis
            test_start_time=time.time() #Start test duration time
            throughput=CapacityAnalysis_obj.automatedLoadTesting() #Start Capacity Analysis Mechanism to cpature the maximum throughput at single core level
            test_end_time=time.time() #End test duration time
            self.maxThroughput_vs_cores[cores]=throughput #Capture maximum throughput and resource usage
            self.metrics_vs_cores["Throughput"][cores]=self.maxThroughput_vs_cores[cores]
            self.metrics_vs_cores["responseTime"][cores]=CapacityAnalysis_obj.max_response_time
            self.metrics_vs_cores["failureRate"][cores]=CapacityAnalysis_obj.max_failure_rate
            self.metrics_vs_cores["observedThinkTime"][cores]=CapacityAnalysis_obj.max_observed_think_time
            self.metrics_vs_cores["OverallCPUPercentage"][cores]=CapacityAnalysis_obj.application_resource_usage["OverallCPUPercentage"]
            self.metrics_vs_cores["userCPUTime"][cores]=CapacityAnalysis_obj.application_resource_usage["userCPUTime"]
            self.metrics_vs_cores["sysCPUTime"][cores]=CapacityAnalysis_obj.application_resource_usage["sysCPUTime"]
            self.metrics_vs_cores["ctxSwitches"][cores]=CapacityAnalysis_obj.application_resource_usage["ctxSwitches"]
            self.metrics_vs_cores["virtualMemoryUsedPercentage"][cores]=CapacityAnalysis_obj.application_resource_usage["virtualMemoryUsedPercentage"]
            self.metrics_vs_cores["diskUsedPercentage"][cores]=CapacityAnalysis_obj.application_resource_usage["diskUsedPercentage"]
            self.metrics_vs_cores["swapMemoryUsedPercentage"][cores]=CapacityAnalysis_obj.application_resource_usage["swapMemoryUsedPercentage"]
            self.metrics_vs_cores["calculatedCPUServiceDemand"][cores]=(cores*self.metrics_vs_cores["OverallCPUPercentage"][cores])/(self.metrics_vs_cores["Throughput"][cores]*100)
            self.metrics_vs_cores["observedCPUServiceDemand"][cores]=0
            self.metrics_vs_cores["test-duration"][cores]=test_end_time-test_start_time
            count=0
            print(CapacityAnalysis_obj.process_resource_usage)
            for process_name in processes_details["names"]:
                self.processMetrics_vs_cores[process_name]["cpu_service_demad"][cores]=CapacityAnalysis_obj.max_processes_cpu_service_demad[count]
                self.processMetrics_vs_cores[process_name]["CPUPercentage"][cores]=(CapacityAnalysis_obj.process_resource_usage[process_name]["CPUPercentage"])/cores
                self.processMetrics_vs_cores[process_name]["#_of_worker_processes_threads"][cores]=(CapacityAnalysis_obj.process_resource_usage[process_name]["#_of_worker_processes_threads"])
                self.processMetrics_vs_cores[process_name]["memory_percentage"][cores]=(CapacityAnalysis_obj.process_resource_usage[process_name]["memory_percentage"])
                self.metrics_vs_cores["observedCPUServiceDemand"][cores]=self.metrics_vs_cores["observedCPUServiceDemand"][cores]+self.processMetrics_vs_cores[process_name]["cpu_service_demad"][cores]
                count=count+1
        
        #Scalability Profiling Inference
        [scalability_limit_core,scalability_core,scalability_factor_core,application_no_core_scalability]=self.scalabilityInterpretation(cores_details)

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


        self.scalabilityAnalysis(scalability_limit_core,scalability_core,scalability_factor_core,application_no_core_scalability,cores_details,processes_details) #Scalability Analysis
    
    def scalabilityInterpretation(self,cores_details):
        scalability_limit_core=[]
        scalability_core=[]
        scalability_factor_core=[]
        application_core_scalability=1
        for n_cores in cores_details['cores']:
            if (self.maxThroughput_vs_cores[n_cores]/self.maxThroughput_vs_cores[1]) >= (cores_details['scalabilityToleranceFactor']*(n_cores)): #Scalability Tolerance Factor
                application_core_scalability=n_cores #N_s
                scalability_core.append(n_cores)
            else:
                scalability_limit_core.append(n_cores)
            scalability_factor_core.append(self.maxThroughput_vs_cores[n_cores]/self.maxThroughput_vs_cores[1])
        
        self.plotScalabilityGraph()

        if application_core_scalability==cores_details['cores'][-1]: #If N_s == c_max
            print("Application is Scaling")
            return [scalability_limit_core,scalability_core,scalability_factor_core,application_core_scalability]
        else:
            temp=cores_details['cores'].index(application_core_scalability)
            print("Application is not scaling from "+str(cores_details['cores'][temp+1])+" cores with scalability factor "+ str(scalability_factor_core[temp+1])) #N_b
            print("Application is scaling till "+str(application_core_scalability)+" cores") #N_s
            return [scalability_limit_core,scalability_core,scalability_factor_core,cores_details['cores'][temp+1]]

    def scalabilityAnalysis(self,scalability_limit_core,scalability_core,scalability_factor_core,application_no_core_scalability,cores_details,processes_details):
        output_file_name=self.load_test_folder+"/"+"scalabilityAnalysis.csv"
        flattened_processMetrics_vs_cores = {}
        for key1, sub_dict in self.processMetrics_vs_cores.items():
            for key2, values in sub_dict.items():
                flattened_processMetrics_vs_cores[f"{key1}_{key2}"] = values
        
        df1 = pd.DataFrame(self.metrics_vs_cores)
        df2 = pd.DataFrame(flattened_processMetrics_vs_cores)

        metric_data_vs_cores = pd.concat([df1, df2], axis=1)

        metric_data_vs_cores.index.name = '# of cores'
        metric_data_vs_cores.reset_index(inplace=True)

        metric_data_vs_cores['scaling'] = metric_data_vs_cores['# of cores'].apply(lambda x: 'yes' if x in scalability_core else ('no' if x in scalability_limit_core else None))

        metric_data_vs_cores['scaling_factor'] = scalability_factor_core

        metric_data_vs_cores.to_csv(output_file_name, index=False)

        #Is CPU core are bottleneck at N_b
        if (self.metrics_vs_cores["OverallCPUPercentage"][application_no_core_scalability]) < 90:
            print("CPU cores are not the bottleneck at "+str(application_no_core_scalability)+" cores")
        else:
            print("CPU cores might be the bottleneck at "+str(application_no_core_scalability)+" cores")
        
        #Service Demand Inflation
        service_demand_no_inlflation_core=cores_details['cores'][-1]
        service_demand_inlfation_factor={}
        for n_cores in cores_details['cores']:
            if (self.metrics_vs_cores["calculatedCPUServiceDemand"][n_cores]/self.metrics_vs_cores["calculatedCPUServiceDemand"][1]) <= (cores_details['serviceDemandInflationFactor']):
                service_demand_no_inlflation_core=n_cores
            service_demand_inlfation_factor[n_cores]=self.metrics_vs_cores["calculatedCPUServiceDemand"][n_cores]/self.metrics_vs_cores["calculatedCPUServiceDemand"][1]

        if service_demand_no_inlflation_core==cores_details['cores'][-1]:
            print("No CPU service demand inflation")
        else:
            temp=cores_details['cores'].index(service_demand_no_inlflation_core)
            print("CPU service demand inflation is seen at "+str(cores_details['cores'][temp+1])+" cores with inlfation factor "+str(service_demand_inlfation_factor[cores_details['cores'][temp+1]]))

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
