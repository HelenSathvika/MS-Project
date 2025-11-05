import sys
import os
import json
import multiprocessing
from multiprocessing import Process, Manager
import time
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import re
import subprocess

class ManualLoadTestingTimeDurationKit():

    manual_conf={}
    throughput=[]
    response_time=[]
    failure_rate=[]
    load_test_folder=""
    load_levels=[]

    def start(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.load_test_folder = "manual_load_test_time_output"+"/"+"loadTesting_"+timestamp 
        os.makedirs(self.load_test_folder)
        manual_configurations="input-configurations/manual-load-testing-time-conf.json"
        with open(manual_configurations,'rb') as file:
            manual_conf_content=file.read()
        manual_conf_json_content=manual_conf_content.decode('utf-8')
        self.manual_conf=json.loads(manual_conf_json_content)
        self.runLoadTest()
    
    def runLoadTest(self):
        load_generator_details=self.manual_conf['loadGeneratorDetails']
        self.load_levels=self.manual_conf['loadLevels']
        user_session=self.manual_conf['sessionDetails']
        test_duration=self.manual_conf['testDuration']

        with open('TaurusSessionDescriptionFile.yaml','r+') as file:
            taurus_session_description_file_content=file.read()
            taurus_session_description_file_content=re.sub(r'(executor:\s+)[A-z]+(.*)',rf'\g<1>{load_generator_details["loadGenerator"]}\g<2>',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(script:\s+).*',rf'\g<1>{user_session["filePath"]}',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(hold-for:\s+)[0-9]+[a-zA-Z]*', rf'\g<1>{test_duration}',taurus_session_description_file_content)
        with open('TaurusSessionDescriptionFile.yaml','w') as file:
            file.write(taurus_session_description_file_content)

        for load_level in self.load_levels:
            self.runOneLoadLevel(load_level)
        
        self.plotmetricsGraph("Throughput_vs_Load_Level",self.throughput,"Throughput(req/sec)")
        self.plotmetricsGraph("Response_Time_vs_Load_Level",self.response_time,"Response Time(msec)")
        self.plotmetricsGraph("Failue_Rate_vs_Load_Level",self.failure_rate,"Failure Rate")
    
    def runOneLoadLevel(self,load_level):
        
        with open('TaurusSessionDescriptionFile.yaml','r') as file:
            file_content=file.read()
            file_content=re.sub(r'(concurrency:\s+)[0-9]+(.*)',rf'\g<1>{load_level}\g<2>',file_content)
        with open('TaurusSessionDescriptionFile.yaml','w') as file:
            file.write(file_content)

        process=subprocess.Popen("bzt TaurusSessionDescriptionFile.yaml",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        flag=True
        while flag:
            for line in process.stdout:
                taurus_log_folder_match=re.search(r"(?:INFO: Artifacts dir: )(.+)",line.strip())
                if taurus_log_folder_match:
                    taurus_log_folder_path=taurus_log_folder_match.group(1)
                    taurus_log_folder_path=taurus_log_folder_path+"/kpi.jtl"
                    break
            flag=False
        stdout, stderr = process.communicate()
        
        success_pattern = r"(\d+) succ"
        failure_pattern = r"(\d+) fail"
        response_time_pattern = r"(\d+\.\d+) avg rt"
        
        data = pd.read_csv(taurus_log_folder_path)
        test_duration = data['timeStamp'].max() - data['timeStamp'].min()
        total_requests = len(data)
        successful_requests = data['success'].sum()
        failed_requests = total_requests-successful_requests
        throughput_load = successful_requests/test_duration
        avg_response_time = data['elapsed'].mean()
        avg_failure_rate = failed_requests/total_requests * 100

        self.throughput.append(throughput_load*1000)
        self.response_time.append(avg_response_time)
        self.failure_rate.append(avg_failure_rate)


    def plotmetricsGraph(self,plot_title,y_axis,y_axis_title):

        file_name=self.load_test_folder+"/"+plot_title
        x_axis=self.load_levels
        plt.figure(figsize=(8, 5))
        plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b', label='Values')
        plt.xlabel('Load Levels')
        plt.ylabel(y_axis_title)
        plt.title(plot_title)
        plt.grid(True)
        plt.ylim(min(y_axis)*0.9,max(y_axis)*1.1)
        plt.savefig(file_name)
        plt.close()


