#!/usr/bin/env python3
import math
class AutoPerf:
    
    think_time=""
    cores=""
    load_generator_master_obj=""
    profiling_agent_master_obj=""
    max_throughput=0
    application_resource_usage={}
    process_resource_usage={}
    process_perf_resource_usage={}
    application_perf_resource_usage={}
    max_response_time=0
    max_failure_rate=0
    max_observed_think_time=0
    max_processes_cpu_service_demad=[]


    def initialize(self,think_time,active_cores,load_generator_master_obj,profiling_agent_master_obj):
        self.think_time=think_time
        self.cores=active_cores
        self.load_generator_master_obj=load_generator_master_obj
        self.profiling_agent_master_obj=profiling_agent_master_obj
    
    def automatedLoadTesting(self):
        #autoperf algorithm for automated load testing
        (min_load,cpu_service_demands)=self.minimumLoadLevel()
        max_load=self.maximumLoadLevel(cpu_service_demands)
        range_start=min_load
        range_end=max_load
        while range_start<range_end:
            (range_mid,cpu_service_demands)=self.runOptimalInRange(range_start,range_end)
            range_start=range_end+1
            range_end=self.maximumLoadLevel(cpu_service_demands)

        (load_level_too_low,throughput1,response_time1,failure_rate1,observed_thinktime1,all_cpu_service_demands1,application_resource_usage1,process_resource_usage1,perf_application_resource_usage1,perf_process_resource_usage1)=self.load_generator_master_obj.runOneLoadLevel(range_end+1)
        self.saveMaxThroughput(throughput1,response_time1,failure_rate1,observed_thinktime1,all_cpu_service_demands1,application_resource_usage1,process_resource_usage1,perf_application_resource_usage1,perf_process_resource_usage1)
        temp=1.3
        load_level=int(math.ceil(temp*range_end))
        while True:
            (load_level_too_low,throughput2,response_time2,failure_rate2,observed_thinktime2,all_cpu_service_demands2,application_resource_usage2,process_resource_usage2,perf_application_resource_usage2,perf_process_resource_usage2)=self.load_generator_master_obj.runOneLoadLevel(load_level)
            self.saveMaxThroughput(throughput2,response_time2,failure_rate2,observed_thinktime2,all_cpu_service_demands2,application_resource_usage2,process_resource_usage2,perf_application_resource_usage2,perf_process_resource_usage2)
            load_level=int(math.ceil(temp*load_level))
            if((abs(throughput2-throughput1)/throughput1)<=0.1) or throughput2<=(0.1*throughput1) :
                break
            throughput1=throughput2
        return self.max_throughput

    def minimumLoadLevel(self):
        load_level=1
        min_found=False
        while not min_found:
            (load_level_too_low,throughput,response_time,error_rate,observed_thinktime,all_cpu_service_demands,application_resource_usage,process_resource_usage,perf_application_resource_usage,perf_process_resource_usage)=self.load_generator_master_obj.runOneLoadLevel(load_level)
            print(throughput)
            print(response_time)
            if load_level_too_low:
                if(max(all_cpu_service_demands)>0):
                    min_load=0.1*((self.think_time+response_time)/max(all_cpu_service_demands))*self.cores
                else:
                    min_load=load_level
                if min_load<=load_level:
                    min_load=max(1.1*load_level,load_level+1)
                load_level=int(min_load)
            else:
                min_found=True
        self.saveMaxThroughput(throughput,response_time,error_rate,observed_thinktime,all_cpu_service_demands,application_resource_usage,process_resource_usage,perf_application_resource_usage,perf_process_resource_usage)
        return (load_level,all_cpu_service_demands)

    def maximumLoadLevel(self,all_cpu_service_demands):
        max_load=int(((self.think_time+sum(all_cpu_service_demands))/max(all_cpu_service_demands))*self.cores)
        return max_load

    def runOptimalInRange(self,min_load,max_load):
        if(min_load==max_load):
            (load_level_too_low,throughput,response_time,failure_rate,observed_thinktime,all_cpu_service_demands,application_resource_usage,process_resource_usage,perf_application_resource_usage,perf_process_resource_usage)=self.load_generator_master_obj.runOneLoadLevel(min_load)
            return (min_load,all_cpu_service_demands)
        (load_level_too_low,throughput1,response_time1,failure_rate1,observed_thinktime1,all_cpu_service_demands1,application_resource_usage1,process_resource_usage1,perf_application_resource_usage1,perf_process_resource_usage1)=self.load_generator_master_obj.runOneLoadLevel(min_load)
        (load_level_too_low,throughput2,response_time2,failure_rate2,observed_thinktime2,all_cpu_service_demands2,application_resource_usage2,process_resource_usage2,perf_application_resource_usage2,perf_process_resource_usage2)=self.load_generator_master_obj.runOneLoadLevel(max_load)
        (load_level_too_low,throughput3,response_time3,failure_rate3,observed_thinktime3,all_cpu_service_demands3,application_resource_usage3,process_resource_usage3,perf_application_resource_usage2,perf_process_resource_usage2)=self.load_generator_master_obj.runOneLoadLevel(int((min_load+max_load)/2))
        self.saveMaxThroughput(throughput1,response_time1,failure_rate1,observed_thinktime1,all_cpu_service_demands1,application_resource_usage1,process_resource_usage1,perf_application_resource_usage1,perf_process_resource_usage1)
        self.saveMaxThroughput(throughput2,response_time2,failure_rate2,observed_thinktime2,all_cpu_service_demands2,application_resource_usage2,process_resource_usage2,perf_application_resource_usage2,perf_process_resource_usage2)
        self.saveMaxThroughput(throughput3,response_time3,failure_rate3,observed_thinktime3,all_cpu_service_demands3,application_resource_usage3,process_resource_usage3,perf_application_resource_usage2,perf_process_resource_usage2)
        if abs(throughput3-((throughput1+throughput2)/2))<5:
            return (int((min_load+max_load)/2),all_cpu_service_demands3)
        else:
            self.runOptimalInRange(min_load,int((min_load+max_load)/2))
            (mid,all_cpu_service_demands3)=self.runOptimalInRange(int((min_load+max_load)/2)+1,max_load)
        return (mid,all_cpu_service_demands3)

    def saveMaxThroughput(self,throughput,response_time,error_rate,observed_thinktime,all_cpu_service_demands,application_resource_usage,process_resource_usage,perf_application_resource_usage,perf_process_resource_usage):
        if self.max_throughput<=throughput:
            self.max_throughput=throughput
            self.application_resource_usage=application_resource_usage
            self.process_resource_usage=process_resource_usage
            self.process_perf_resource_usage=perf_process_resource_usage
            self.application_perf_resource_usage=perf_application_resource_usage
            self.max_response_time=response_time
            self.max_failure_rate=error_rate
            self.max_observed_think_time=observed_thinktime
            self.max_processes_cpu_service_demad=all_cpu_service_demands