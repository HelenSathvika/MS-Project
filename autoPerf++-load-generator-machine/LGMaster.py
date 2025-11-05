#!/usr/bin/env python3
import subprocess
import psutil
import multiprocessing
import re
import datetime
from datetime import datetime
import time
from multiprocessing import Process, Manager
import matplotlib.pyplot as plt
import threading

class LGMaster:

    no_of_requests_completed=0
    number_of_failure_requests=0
    throughput_list=[]
    failure_rate_list=[]
    responsetime_list=[]
    time_stamp_list=[]
    taurus_log_folder_path=""
    flag_calulate_number_of_requests=""
    profiling_agent_obj=""
    mode=""

    def initialize(self,lg,session_description,profiling_agent_obj,mode):

        #modify the lg and session description
        
        with open('TaurusSessionDescriptionFile.yaml','r+') as file:
            taurus_session_description_file_content=file.read()
            taurus_session_description_file_content=re.sub(r'(executor:\s+)[A-z]+(.*)',rf'\g<1>{lg}\g<2>',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(script:\s+).*',rf'\g<1>{session_description}',taurus_session_description_file_content)
        with open('TaurusSessionDescriptionFile.yaml','w') as file:
            file.write(taurus_session_description_file_content)

        self.profiling_agent_obj=profiling_agent_obj
        self.mode=mode

    def runOneLoadLevel(self,load_level):
        

        time.sleep(120)

        self.throughput_list=[]
        self.failure_rate_list=[]
        self.responsetime_list=[]
        self.time_stamp_list=[]
        self.taurus_log_folder_path=""
        self.flag_calulate_number_of_requests=True

        #Change load level
        with open('TaurusSessionDescriptionFile.yaml','r') as file:
            file_content=file.read()
            file_content=re.sub(r'(concurrency:\s+)[0-9]+(.*)',rf'\g<1>{load_level}\g<2>',file_content)
        with open('TaurusSessionDescriptionFile.yaml','w') as file:
            file.write(file_content)


        #start Taurus
        process=subprocess.Popen("bzt TaurusSessionDescriptionFile.yaml",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

        self.profiling_agent_obj.startProfilingAgentAtServer()
        if self.mode=="perfProfiling":
            self.profiling_agent_obj.startPerfProfilingAtServer()

        count=5
        flag=True
        load_test_start_time=""

        #throughput convergence
        while flag:
            for line in process.stdout:
                if not load_test_start_time:
                    load_test_start_time_match=re.search(r"(\d{2}:\d{2}:\d{2}) INFO: Current",line.strip())
                if load_test_start_time_match:
                    load_test_start_time=datetime.strptime(load_test_start_time_match.group(1),'%H:%M:%S')
                
                time_stamp_match=re.search(r"(\d{2}:\d{2}:\d{2})",line.strip())
                success_match=re.search(r"(\d+) succ",line.strip())
                failure_match=re.search(r"(\d+) fail",line.strip())
                responsetime_match=re.search(r"(\d+\.\d+) avg rt",line.strip())
                taurus_log_folder_match=re.search(r"(?:INFO: Artifacts dir: )(.+)",line.strip())
                if self.taurus_log_folder_path=="":
                    if taurus_log_folder_match:
                        self.taurus_log_folder_path=taurus_log_folder_match.group(1)
                        self.taurus_log_folder_path=self.taurus_log_folder_path+"/kpi.jtl"

                if time_stamp_match and success_match:
                    time_stamp=datetime.strptime(time_stamp_match.group(1),'%H:%M:%S')
                    total_latency=0
                    no_of_requests_completed=0
                    time_stamp0=0
                    with open(self.taurus_log_folder_path,"r") as file:
                        next(file)
                        for line in file:
                            data=line.split(',')
                            if data[6]=='true':
                                latency=int(data[10])
                                no_of_requests_completed=no_of_requests_completed+1
                                total_latency=total_latency+latency
                                if(time_stamp0==0):
                                    time_stamp0=int(data[0])
                                time_stamp1=int(data[0])
                    self.no_of_requests_completed=no_of_requests_completed
                    self.number_of_failure_requests=self.number_of_failure_requests+int(failure_match.group(1))
                    responsetime=float(responsetime_match.group(1))
                    if (time_stamp-load_test_start_time).total_seconds() == 0:
                        self.throughput_list.append(0)
                        self.failure_rate_list.append(0)
                        self.responsetime_list.append((total_latency/self.no_of_requests_completed)*0.001)
                        self.time_stamp_list.append(0)    
                    else:
                        throughput=self.no_of_requests_completed/((time_stamp1-time_stamp0)*0.001)
                        failure_rate=self.number_of_failure_requests/(time_stamp-load_test_start_time).total_seconds()
                        self.throughput_list.append(throughput)
                        self.failure_rate_list.append(failure_rate)
                        self.responsetime_list.append((total_latency/self.no_of_requests_completed)*0.001)
                        self.time_stamp_list.append((time_stamp1-time_stamp0)*0.001)

                    if len(self.throughput_list)<=2:
                        continue
                    if (self.throughput_list[-2]==0):
                        continue
                    if (abs(self.throughput_list[-1]-self.throughput_list[-2])/self.throughput_list[-2]) <= 0.1:
                        count=count-1
                        if count==0:
                            flag=False
                            break
                    else:
                        count=5

        self.profiling_agent_obj.stopProfilingAgentAtServer()
        self.profiling_agent_obj.startGettingCPUTime()

        threading.Thread(target=self.calculateNoOfRequests,args=(process.stdout,load_test_start_time,)).start()

        temp_completed_requests=self.no_of_requests_completed
        temp_completed_requests1=self.no_of_requests_completed
        process_service_demand=[0]*len(self.profiling_agent_obj.process_names)
        temp_process_service_demand=[0]*len(self.profiling_agent_obj.process_names)
        temp_cpu_time=[0]*len(self.profiling_agent_obj.process_names)
        count=[5]*len(self.profiling_agent_obj.process_names)

        while True:
            time.sleep(2)
            temp_completed_requests1=temp_completed_requests1+self.no_of_requests_completed
            [cpu_time_list,cpu_percentage]=self.profiling_agent_obj.getCPUTime()
            temp_completed_requests=temp_completed_requests+self.no_of_requests_completed
            temp=(temp_completed_requests1-temp_completed_requests)/2
            for i in range(0,len(self.profiling_agent_obj.process_names)):
                temp_cpu_time[i]=temp_cpu_time[i]+cpu_time_list[i]
            if sum(cpu_percentage)<=0.1:
                self.flag_calulate_number_of_requests=False
                for proc in psutil.process_iter(['name']):
                    if proc.info['name']=="bzt":
                        proc.kill()
                    if proc.info['name']=="java":
                        proc.kill()
                application_resource_usage=self.profiling_agent_obj.getApplicationResourceUsage()
                print(application_resource_usage)
                process_resource_usage=self.profiling_agent_obj.getprocessResourceUsage()
                print(process_resource_usage)
                perf_application_resource_usage={}
                perf_process_resource_usage={}
                if self.mode=="perfProfiling":
                    perf_application_resource_usage=self.profiling_agent_obj.getPerfApplicationResourceUsage()
                    perf_process_resource_usage=self.profiling_agent_obj.getPerfProcessResourceUsage()
                    self.profiling_agent_obj.stopPerfProfilingAgentAtServer()
                
                self.profiling_agent_obj.stopProfilingAgentAtServer()
                for i in range(0,len(self.profiling_agent_obj.process_names)):
                    temp_process_service_demand[i]=(temp_cpu_time[i])/(temp_completed_requests1+temp)
                test_end_time=time.time()
                test_elapsed_time=test_end_time-test_start_time
                observerd_thinktime=(load_level/self.throughput_list[-1])-self.responsetime_list[-1]
                return (True,self.throughput_list[-1],self.responsetime_list[-1],self.failure_rate_list[-1],observerd_thinktime,temp_process_service_demand,application_resource_usage,process_resource_usage,perf_application_resource_usage,perf_process_resource_usage)
            for i in range(0,len(self.profiling_agent_obj.process_names)):
                temp_process_service_demand[i]=(temp_cpu_time[i])/(temp_completed_requests1+temp)
            for i in range(0,len(self.profiling_agent_obj.process_names)):
                if (abs(temp_process_service_demand[i]-process_service_demand[i]))<=0.009:
                    count[i]=count[i]-1
                else:
                    count[i]=5
            if sum(count)<=0:
                break
            for i in range(0,len(temp_process_service_demand)):
                process_service_demand[i]=temp_process_service_demand[i]

        self.flag_calulate_number_of_requests=False

        for proc in psutil.process_iter(['name']):
            if proc.info['name']=="bzt":
                proc.kill()
            if proc.info['name']=="java":
                proc.kill()

        application_resource_usage=self.profiling_agent_obj.getApplicationResourceUsage()
        process_resource_usage=self.profiling_agent_obj.getprocessResourceUsage()
        perf_application_resource_usage={}
        perf_process_resource_usage={}
        if self.mode=="perfProfiling":
            perf_application_resource_usage=self.profiling_agent_obj.getPerfApplicationResourceUsage()
            perf_process_resource_usage=self.profiling_agent_obj.getPerfProcessResourceUsage()
            self.profiling_agent_obj.stopPerfProfilingAgentAtServer()

        self.profiling_agent_obj.stopProfilingAgentAtServer()
        
        observerd_thinktime=(load_level/self.throughput_list[-1])-self.responsetime_list[-1]
        time.sleep(100)
        return (False,self.throughput_list[-1],self.responsetime_list[-1],self.failure_rate_list[-1],observerd_thinktime,temp_process_service_demand,application_resource_usage,process_resource_usage,perf_application_resource_usage,perf_process_resource_usage)

    def calculateNoOfRequests(self,process_stdout,load_test_start_time):
        time.sleep(1)
        while self.flag_calulate_number_of_requests:
            for line in process_stdout:
                time_stamp_match=re.search(r"(\d{2}:\d{2}:\d{2})",line.strip())
                success_match=re.search(r"(\d+) succ",line.strip())
                failure_match=re.search(r"(\d+) fail",line.strip())
                responsetime_match=re.search(r"(\d+\.\d+) avg rt",line.strip())
                if time_stamp_match and success_match:
                    time_stamp=datetime.strptime(time_stamp_match.group(1),'%H:%M:%S')
                    total_latency=0
                    no_of_requests_completed=0
                    time_stamp0=0
                    with open(self.taurus_log_folder_path,"r") as file:
                        next(file)
                        next(file)
                        for line in file:
                            data=line.split(',')
                            if data[6]=='true':
                                latency=int(data[10])
                                no_of_requests_completed=no_of_requests_completed+1
                                total_latency=total_latency+latency
                                if(time_stamp0==0):
                                    time_stamp0=int(data[0])
                                time_stamp1=int(data[0])
                    self.no_of_requests_completed=no_of_requests_completed
                    self.number_of_failure_requests=self.number_of_failure_requests+int(failure_match.group(1))
                    responsetime=float(responsetime_match.group(1))
                    throughput=self.no_of_requests_completed/((time_stamp1-time_stamp0)*0.001)
                    failure_rate=self.number_of_failure_requests/(time_stamp-load_test_start_time).total_seconds()
                    self.throughput_list.append(throughput)
                    self.failure_rate_list.append(failure_rate)
                    self.responsetime_list.append((total_latency/self.no_of_requests_completed)*0.001)
                    self.time_stamp_list.append((time_stamp1-time_stamp0)*0.001)

                if self.flag_calulate_number_of_requests:
                    break
            time.sleep(1)
