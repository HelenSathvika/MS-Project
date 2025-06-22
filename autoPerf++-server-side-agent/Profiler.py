import psutil
import time
import threading
import subprocess
import re
import concurrent.futures
import os

class Profiler:

    process_names=[]
    process_resource_usage={}
    background_resource_usage={}
    capture_metrics_flag=""
    resource_usage_application={}
    background_resource_usage_system={}

    def start(self,process_names): #Start Profiler
        self.process_names=process_names
        self.capture_metrics_flag=True
        for process_name in process_names: #Capture resource uasge
            self.process_resource_usage[process_name]={"CPUTime":0,"CPUPercentage":0,"#_of_worker_processes_threads":0,"memory_percentage":0}
            self.background_resource_usage[process_name]={"CPUTime":0,"CPUPercentage":0,"#_of_worker_processes_threads":0,"memory_percentage":0}
        self.resource_usage_application={"OverallCPUPercentage":0,"perCPUPercentage":[],"userCPUTime":0,"sysCPUTime":0,"ctxSwitches":0,"virtualMemoryUsedPercentage":0,"diskUsedPercentage":0,"swapMemoryUsedPercentage":0}
        self.background_resource_usage_system={"OverallCPUPercentage":0,"perCPUPercentage":[],"userCPUTime":0,"sysCPUTime":0,"ctxSwitches":0,"virtualMemoryUsedPercentage":0,"diskUsedPercentage":0,"swapMemoryUsedPercentage":0}

        for process_name in process_names:
            cpu_time=0
            cpu_percentage=0
            num_worker_processes_threads=0
            for proc in psutil.process_iter(['pid','name','ppid']): #Capture resource used eailer for each proc using either name or pid or parent id
                if (proc.info['name'] == process_name or (process_name.isdigit() and (proc.info['pid'] == int(process_name) or proc.info['ppid'] == int(process_name)))):
                    cpu_time=cpu_time+sum(proc.cpu_times()[:2]) #Capture CPU Time (user and system)
                    cpu_percentage=cpu_percentage+proc.cpu_percent(interval=None) #CPU percentage
                    num_worker_processes_threads=num_worker_processes_threads+proc.num_threads()
            self.background_resource_usage[process_name]["CPUTime"]=cpu_time
            self.background_resource_usage[process_name]["CPUPercentage"]=cpu_percentage
            self.background_resource_usage[process_name]["#_of_worker_processes_threads"]=num_worker_processes_threads
        self.background_resource_usage_system["userCPUTime"]=psutil.cpu_times().user #Capture system user cpu time
        self.background_resource_usage_system["sysCPUTime"]=psutil.cpu_times().system #Capture system system CPU time
        self.background_resource_usage_system["ctxSwitches"]=psutil.cpu_stats().ctx_switches #Capture number of context switches

        threading.Thread(target=self.captureMetrics).start() #Start capturing resource usage metrics

    def captureMetrics(self): #Start capturing resource uasge metrics
        while self.capture_metrics_flag: 
            time.sleep(1) #Sleep for 1 sec and capture again 
            for process_name in self.process_names:
                cpu_time=0
                cpu_percentage=0
                num_worker_processes_threads=0
                for proc in psutil.process_iter(['pid','name','ppid']): #Capture resource usage for each proc using either name or pid or parent id
                    if (proc.info['name'] == process_name or (process_name.isdigit() and (proc.info['pid'] == int(process_name) or proc.info['ppid'] == int(process_name)))):
                        cpu_time=cpu_time+sum(proc.cpu_times()[:2])
                        cpu_percentage=cpu_percentage+proc.cpu_percent(interval=None)
                        num_worker_processes_threads=num_worker_processes_threads+proc.num_threads()
                self.process_resource_usage[process_name]["CPUTime"]=cpu_time-self.background_resource_usage[process_name]["CPUTime"] #Remove background resource usage
                self.process_resource_usage[process_name]["CPUPercentage"]=max(cpu_percentage,self.process_resource_usage[process_name]["CPUPercentage"])
                self.process_resource_usage[process_name]["#_of_worker_processes_threads"]=max(num_worker_processes_threads,self.process_resource_usage[process_name]["#_of_worker_processes_threads"])
                self.process_resource_usage[process_name]["memory_percentage"]=max(self.process_resource_usage[process_name]["memory_percentage"],proc.memory_percent())
            self.resource_usage_application["OverallCPUPercentage"]=max(self.resource_usage_application["OverallCPUPercentage"],psutil.cpu_percent(interval=None))
            self.resource_usage_application["perCPUPercentage"]=psutil.cpu_percent(interval=None,percpu=True)
            self.resource_usage_application["userCPUTime"]=psutil.cpu_times().user-self.background_resource_usage_system["userCPUTime"]
            self.resource_usage_application["sysCPUTime"]=psutil.cpu_times().system-self.background_resource_usage_system["sysCPUTime"]
            self.resource_usage_application["ctxSwitches"]=psutil.cpu_stats().ctx_switches-self.background_resource_usage_system["ctxSwitches"]
            self.resource_usage_application["virtualMemoryUsedPercentage"]=max(self.resource_usage_application["virtualMemoryUsedPercentage"],psutil.virtual_memory().percent)
            self.resource_usage_application["diskUsedPercentage"]=max(self.resource_usage_application["diskUsedPercentage"],psutil.disk_usage('/').percent)
            self.resource_usage_application["swapMemoryUsedPercentage"]=max(self.resource_usage_application["swapMemoryUsedPercentage"],psutil.swap_memory().percent)
    
    def startGettingCPUTime(self): #Start Getting CPU Time
        self.capture_metrics_flag=False

    def getCPUTime(self): #Return only CPU Time
        for process_name in self.process_names:
            cpu_time=0
            cpu_percentage=0
            num_worker_processes_threads=0
            for proc in psutil.process_iter(['pid','name','ppid']):
                if (proc.info['name'] == process_name or (process_name.isdigit() and (proc.info['pid'] == int(process_name) or proc.info['ppid'] == int(process_name)))):
                    cpu_percentage=cpu_percentage+proc.cpu_percent(interval=None)
                    cpu_time=cpu_time+sum(proc.cpu_times()[:2])
                    num_worker_processes_threads=num_worker_processes_threads+proc.num_threads()
            self.process_resource_usage[process_name]["CPUTime"]=cpu_time-self.background_resource_usage[process_name]["CPUTime"]
            self.process_resource_usage[process_name]["CPUPercentage"]=max(cpu_percentage,self.process_resource_usage[process_name]["CPUPercentage"])
            self.process_resource_usage[process_name]["#_of_worker_processes_threads"]=max(num_worker_processes_threads,self.process_resource_usage[process_name]["#_of_worker_processes_threads"])
            self.process_resource_usage[process_name]["memory_percentage"]=max(self.process_resource_usage[process_name]["memory_percentage"],proc.memory_percent())
        self.resource_usage_application["OverallCPUPercentage"]=max(self.resource_usage_application["OverallCPUPercentage"],psutil.cpu_percent(interval=None))
        self.resource_usage_application["perCPUPercentage"]=psutil.cpu_percent(interval=None,percpu=True)
        self.resource_usage_application["userCPUTime"]=psutil.cpu_times().user-self.background_resource_usage_system["userCPUTime"]
        self.resource_usage_application["sysCPUTime"]=psutil.cpu_times().system-self.background_resource_usage_system["sysCPUTime"]
        self.resource_usage_application["ctxSwitches"]=psutil.cpu_stats().ctx_switches-self.background_resource_usage_system["ctxSwitches"]
        self.resource_usage_application["virtualMemoryUsedPercentage"]=max(self.resource_usage_application["virtualMemoryUsedPercentage"],psutil.virtual_memory().percent)
        self.resource_usage_application["diskUsedPercentage"]=max(self.resource_usage_application["diskUsedPercentage"],psutil.disk_usage('/').percent)
        self.resource_usage_application["swapMemoryUsedPercentage"]=max(self.resource_usage_application["swapMemoryUsedPercentage"],psutil.swap_memory().percent)
        cpu_time_list=[]
        cpu_percentage_list=[]
        for process_name in self.process_names: #For each process retur CPU Time and CPU percentage
            cpu_time_list.append(self.process_resource_usage[process_name]["CPUTime"])
            cpu_percentage_list.append(self.process_resource_usage[process_name]["CPUPercentage"])
        return [cpu_time_list,cpu_percentage_list]

    def getApplicationResourceUsage(self): #Return overall application resource uasge
        return self.resource_usage_application

    def getprocessResourceUsage(self): #Return process resource usage
        return self.process_resource_usage

    def stop(self): #Stop Profiling
        self.capture_metrics_flag=False
        time.sleep(60)

   
