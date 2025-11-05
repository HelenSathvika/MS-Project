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

class PotentialProcessBottlenecksKit:

    socket_connect_info=None
    load_test_folder=""
    potential_bottlencks_conf={}

    def start(self,socket_connect_info):

        self.socket_connect_info=socket_connect_info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.load_test_folder = "potential_bottleneck_output"+"/"+"loadTesting_"+timestamp
        os.makedirs(self.load_test_folder)
        potential_bottlencks_configurations="input-configurations/potential-process-bottlenecks-conf.json"
        with open(potential_bottlencks_configurations,'rb') as file:
            potential_bottlencks_conf_content=file.read()
        potential_bottlencks_conf_json_content=potential_bottlencks_conf_content.decode('utf-8')
        self.potential_bottlencks_conf=json.loads(potential_bottlencks_conf_json_content)
        self.runTest()
    
    def runTest(self):
        processes_details=self.potential_bottlencks_conf['processToProfileDetails']
        test_duration=self.potential_bottlencks_conf['testDuration']
        user_session=self.potential_bottlencks_conf['sessionDetails']
        load_generator_details=self.potential_bottlencks_conf['loadGeneratorDetails']
        load_level=self.potential_bottlencks_conf['loadLevel']
        similarity_tolerance_factor=self.potential_bottlencks_conf['similarityToleranceFactor']

        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster()
        profiling_agent_master_obj.initialize(processes_details["process_id"],self.socket_connect_info)


        profiling_agent_master_obj.identifyPotentialProcessBottlenecks(test_duration,"noLoad")


        with open('TaurusSessionDescriptionFile.yaml','r+') as file:
            taurus_session_description_file_content=file.read()
            taurus_session_description_file_content=re.sub(r'(executor:\s+)[A-z]+(.*)',rf'\g<1>{load_generator_details["name"]}\g<2>',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(script:\s+).*',rf'\g<1>{user_session["filePath"]}',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(concurrency:\s+)[0-9]+(.*)',rf'\g<1>{load_level}\g<2>',taurus_session_description_file_content)
            taurus_session_description_file_content=re.sub(r'(hold-for:\s+)[0-9]+[a-zA-Z]*', rf'\g<1>{3*test_duration}',taurus_session_description_file_content)
        with open('TaurusSessionDescriptionFile.yaml','w') as file:
            file.write(taurus_session_description_file_content)

        process=subprocess.Popen("bzt TaurusSessionDescriptionFile.yaml",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

        time.sleep(test_duration)


        profiling_agent_master_obj.identifyPotentialProcessBottlenecks(test_duration,"Load")


        # for proc in psutil.process_iter(['name']):
        #     if proc.info['name']=="bzt":
        #         proc.kill()
        #     if proc.info['name']=="java":
        #         proc.kill()

        test_start_time=time.time()
        process_similarity=profiling_agent_master_obj.similarityCheck()
        test_end_time=time.time()
        print(process_similarity)
        print(test_end_time-test_start_time)
        count=0
        for process, similarity in process_similarity.items():
            if similarity > similarity_tolerance_factor:
                print(processes_details["process_name"][count]+" might not be potential bottleneck")
            count=count+1




