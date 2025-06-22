#!/usr/bin/env python3
import time
import datetime
from datetime import datetime
import sys
import os
import json
import ProfilingAgentMaster
from multiprocessing import Process, Manager
import subprocess
import multiprocessing
import re
import psutil

class ThreadPoolClassificationKit:

    socket_connect_info=None
    load_test_folder=""
    potential_bottlencks_conf={}

    def start(self,socket_connect_info): #Start Thread Pool Classification

        self.socket_connect_info=socket_connect_info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.load_test_folder = "potential_bottleneck_output"+"/"+"loadTesting_"+timestamp #Create a unique name folder to store the ouput graphs of this run
        os.makedirs(self.load_test_folder)
        potential_bottlencks_configurations="input-configurations/thread-pool-classification-conf.json" #Read Thread Pool Classification Input File
        with open(potential_bottlencks_configurations,'rb') as file:
            potential_bottlencks_conf_content=file.read()
        potential_bottlencks_conf_json_content=potential_bottlencks_conf_content.decode('utf-8')
        self.potential_bottlencks_conf=json.loads(potential_bottlencks_conf_json_content)
        self.runTest() #Start the run
    
    def runTest(self):
        processes_details=self.potential_bottlencks_conf['processToProfileDetails']
        test_duration=self.potential_bottlencks_conf['testDuration']
        user_session=self.potential_bottlencks_conf['sessionDetails']
        load_generator_details=self.potential_bottlencks_conf['loadGeneratorDetails']
        load_level=self.potential_bottlencks_conf['loadLevel']

        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster()
        profiling_agent_master_obj.initialize(processes_details["process_id"],self.socket_connect_info)


        profiling_agent_master_obj.threadPoolClassification(test_duration,"noLoad") #Start capturing traces of thread pool at no load 


        with open('TaurusSessionDescriptionFile.yaml','r+') as file:
            taurus_session_description_file_content=file.read()
            taurus_session_description_file_content=re.sub(r'(executor:\s+)[A-z]+(.*)',rf'\g<1>{load_generator_details["name"]}\g<2>',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(script:\s+).*',rf'\g<1>{user_session["filePath"]}',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(concurrency:\s+)[0-9]+(.*)',rf'\g<1>{load_level}\g<2>',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(hold-for:\s+)[0-9]+[a-zA-Z]*', rf'\g<1>{3*test_duration}',taurus_session_description_file_content)
        with open('TaurusSessionDescriptionFile.yaml','w') as file:
            file.write(taurus_session_description_file_content)

        process=subprocess.Popen("bzt TaurusSessionDescriptionFile.yaml",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) #Start load testing

        time.sleep(test_duration)


        profiling_agent_master_obj.threadPoolClassification(test_duration,"Load")  #Start capturing traces of thread pool at load


        for proc in psutil.process_iter(['name']):
            if proc.info['name']=="bzt":
                proc.kill()
            if proc.info['name']=="java":
                proc.kill()

        test_start_time=time.time()
        process_similarity=profiling_agent_master_obj.similarityScore() #Collect similarity score
        test_end_time=time.time()
        print(process_similarity)
        print(test_end_time-test_start_time)
        paired = list(zip(processes_details["process_name"], process_similarity)) #Sort the similarity scores in ascending order
        sorted_pairs = sorted(paired, key=lambda x: x[1])
        sorted_names, sorted_values = zip(*sorted_pairs)
        print("Sorted Process Names:", sorted_names)
        print("Sorted Similarity Scores:", sorted_values)
