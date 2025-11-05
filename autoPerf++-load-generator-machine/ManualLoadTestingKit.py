import sys
import os
import json
import time
import datetime
from datetime import datetime
import LGMaster
import ProfilingAgentMaster
import ServerConfigurationMaster
import pandas as pd
import matplotlib.pyplot as plt

class ManualLoadTestingKit:
    
    manual_conf={}
    load_test_folder=""
    socket_connect_info=None
    metrics_vs_load={"Throughput":{},"OverallCPUPercentage":{},"userCPUTime":{},"sysCPUTime":{},"responseTime":{},"failureRate":{},"observedThinkTime":{},"ctxSwitches":{},"virtualMemoryUsedPercentage":{},"diskUsedPercentage":{},"swapMemoryUsedPercentage":{},"LLC-loads":{},"LLC-load-misses":{},"LLC-stores":{},"LLC-store-misses":{},"page-faults":{},"instructions":{},"branches":{},"branch-misses":{},"test_elapsed_time":{}}
    processMetrics_vs_Load={}

    def start(self,socket_connect_info):
        self.socket_connect_info=socket_connect_info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.load_test_folder = "manual_load_test_output"+"/"+"loadTesting_"+timestamp
        os.makedirs(self.load_test_folder)
        manual_configurations="input-configurations/manual-load-testing-conf.json"
        with open(manual_configurations,'rb') as file:
            manual_conf_content=file.read()
        manual_conf_json_content=manual_conf_content.decode('utf-8')
        self.manual_conf=json.loads(manual_conf_json_content)
        self.runLoadTest()

    def runLoadTest(self):
        load_generator_details=self.manual_conf['loadGeneratorDetails']
        load_levels=self.manual_conf['loadLevels']
        user_session=self.manual_conf['sessionDetails']
        processes_details=self.manual_conf['processToProfileDetails']
        core_details=self.manual_conf['coresDetails']

        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster()

        load_generator_master_obj=LGMaster.LGMaster()
        load_generator_master_obj.initialize(load_generator_details["loadGenerator"],user_session["filePath"],profiling_agent_master_obj)

        profiling_agent_master_obj.initialize(processes_details["names"],self.socket_connect_info)

        for process_name in processes_details["names"]:
            self.processMetrics_vs_Load[process_name]={"cpu_service_demad":{},"CPUPercentage":{},"#_of_worker_processes_threads":{},"memory_percentage":{},"LLC-loads":{},"LLC-load-misses":{},"LLC-stores":{},"LLC-store-misses":{},"page-faults":{},"instructions":{},"branches":{},"branch-misses":{}}

        for load_level in load_levels:
            resource_usage_metrics=load_generator_master_obj.runOneLoadLevel(load_level)
            self.metrics_vs_load["Throughput"][load_level]=resource_usage_metrics[1]
            self.metrics_vs_load["responseTime"][load_level]=resource_usage_metrics[2]
            self.metrics_vs_load["failureRate"][load_level]=resource_usage_metrics[3]
            self.metrics_vs_load["observedThinkTime"][load_level]=resource_usage_metrics[4]
            self.metrics_vs_load["OverallCPUPercentage"][load_level]=resource_usage_metrics[6][0]["OverallCPUPercentage"]
            self.metrics_vs_load["userCPUTime"][load_level]=resource_usage_metrics[6][0]["userCPUTime"]
            self.metrics_vs_load["sysCPUTime"][load_level]=resource_usage_metrics[6][0]["sysCPUTime"]
            self.metrics_vs_load["ctxSwitches"][load_level]=resource_usage_metrics[6][0]["ctxSwitches"]
            self.metrics_vs_load["virtualMemoryUsedPercentage"][load_level]=resource_usage_metrics[6][0]["virtualMemoryUsedPercentage"]
            self.metrics_vs_load["diskUsedPercentage"][load_level]=resource_usage_metrics[6][0]["diskUsedPercentage"]
            self.metrics_vs_load["swapMemoryUsedPercentage"][load_level]=resource_usage_metrics[6][0]["swapMemoryUsedPercentage"]
            self.metrics_vs_load["LLC-loads"][load_level]=resource_usage_metrics[6][1]["LLC-loads"]
            self.metrics_vs_load["LLC-load-misses"][load_level]=resource_usage_metrics[6][1]["LLC-load-misses"]
            self.metrics_vs_load["LLC-stores"][load_level]=resource_usage_metrics[6][1]["LLC-stores"]
            self.metrics_vs_load["LLC-store-misses"][load_level]=resource_usage_metrics[6][1]["LLC-store-misses"]
            self.metrics_vs_load["page-faults"][load_level]=resource_usage_metrics[6][1]["page-faults"]
            self.metrics_vs_load["instructions"][load_level]=resource_usage_metrics[6][1]["instructions"]
            self.metrics_vs_load["branches"][load_level]=resource_usage_metrics[6][1]["branches"]
            self.metrics_vs_load["branch-misses"][load_level]=resource_usage_metrics[6][1]["branch-misses"]
            self.metrics_vs_load["test_elapsed_time"][load_level]=resource_usage_metrics[8]
            count=0
            for process_name in processes_details["names"]:
                self.processMetrics_vs_Load[process_name]["cpu_service_demad"][load_level]=resource_usage_metrics[5][count]
                self.processMetrics_vs_Load[process_name]["CPUPercentage"][load_level]=(resource_usage_metrics[7][0][process_name]["CPUPercentage"])/core_details['activeCores']
                self.processMetrics_vs_Load[process_name]["#_of_worker_processes_threads"][load_level]=(resource_usage_metrics[7][0][process_name]["#_of_worker_processes_threads"])
                self.processMetrics_vs_Load[process_name]["memory_percentage"][load_level]=(resource_usage_metrics[7][0][process_name]["memory_percentage"])
                self.processMetrics_vs_Load[process_name]["LLC-loads"][load_level]=(resource_usage_metrics[7][1][process_name]["LLC-loads"])
                self.processMetrics_vs_Load[process_name]["LLC-load-misses"][load_level]=(resource_usage_metrics[7][1][process_name]["LLC-load-misses"])
                self.processMetrics_vs_Load[process_name]["LLC-stores"][load_level]=(resource_usage_metrics[7][1][process_name]["LLC-stores"])
                self.processMetrics_vs_Load[process_name]["LLC-store-misses"][load_level]=(resource_usage_metrics[7][1][process_name]["LLC-store-misses"])
                self.processMetrics_vs_Load[process_name]["page-faults"][load_level]=(resource_usage_metrics[7][1][process_name]["page-faults"])
                self.processMetrics_vs_Load[process_name]["instructions"][load_level]=(resource_usage_metrics[7][1][process_name]["instructions"])
                self.processMetrics_vs_Load[process_name]["branches"][load_level]=(resource_usage_metrics[7][1][process_name]["branches"])
                self.processMetrics_vs_Load[process_name]["branch-misses"][load_level]=(resource_usage_metrics[7][1][process_name]["branch-misses"])
                count=count+1

        self.saveMetrics(load_levels)
        self.plotGraphs()
    
    def saveMetrics(self,load_levels):

        output_file_name=self.load_test_folder+"/"+"metrics.csv"
        flattened_processMetrics_vs_load = {}
        for key1, sub_dict in self.processMetrics_vs_Load.items():
            for key2, values in sub_dict.items():
                flattened_processMetrics_vs_load[f"{key1}_{key2}"] = values
        
        df1 = pd.DataFrame(self.metrics_vs_load)
        df2 = pd.DataFrame(flattened_processMetrics_vs_load)

        metric_data_vs_load = pd.concat([df1, df2], axis=1)

        metric_data_vs_load.index.name = 'Load Level'
        metric_data_vs_load.reset_index(inplace=True)

        metric_data_vs_load.to_csv(output_file_name, index=False)

    def plotGraphs(self):
        csv_file_path = os.path.join(self.load_test_folder, "metrics.csv")
        data = pd.read_csv(csv_file_path)
        x_axis = data.iloc[:, 0].to_numpy()

        for y_column in data.columns[1:]:
            y_axis = data[y_column].to_numpy()
            plt.figure(figsize=(8, 5))
            plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b')
            plt.xlabel(data.columns[0])
            plt.ylabel(y_column)
            plt.title(f"{y_column} vs {data.columns[0]}")
            plt.grid(True)

            if y_axis.min() == y_axis.max():
                buffer = 0.1 * abs(y_axis.min()) if y_axis.min() != 0 else 1.0
                plt.ylim(y_axis.min() - buffer, y_axis.max() + buffer)
            else:
                plt.ylim(y_axis.min() * 0.9, y_axis.max() * 1.1)

            file_name = os.path.join(self.load_test_folder, f"{y_column}_vs_{data.columns[0]}.png")
            plt.savefig(file_name)
            plt.close()

            
    
    
